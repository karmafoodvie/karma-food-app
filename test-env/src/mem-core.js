// Datenbank-Ersatz in reinem JavaScript (kein Server, kein WASM) für die eigenständige Test-Seite.
// Gleiche Schnittstelle wie core.js: makeMem(META, DATA, onChange) -> { handle(req) => {status, body, headers} }
// Unterstützt: GET/POST/PATCH/DELETE auf /rest/v1/<tabelle>, rpc/check_store_pin, Filter (eq neq gt gte lt lte like ilike is in ov,
// not., or(), and()), select inkl. Embedding, order, limit/offset/Range, on_conflict + Prefer resolution/return,
// Primär-/Unique-Schlüssel, Not-null, Defaults, Identity. Nicht geprüft: Fremdschlüssel, Check-Constraints.
(function (g) {
  'use strict';
  class HttpError extends Error { constructor(status, message, code) { super(message); this.status = status; this.code = code; } }
  const R = (status, body, headers = {}) => ({ status, body: body === undefined ? '' : (typeof body === 'string' ? body : JSON.stringify(body)), headers });
  const kind = t => /\[\]$/.test(t) ? 'arr' : /^(integer|bigint|smallint)$/.test(t) ? 'int' : /^(numeric|double|real)/.test(t) ? 'num' : t === 'boolean' ? 'bool' : /^jsonb?$/.test(t) ? 'json' : /^timestamp/.test(t) ? 'ts' : 'str';

  function splitTop(s) {
    const parts = []; let d = 0, q = false, cur = '';
    for (const ch of s) { if (ch === '"') q = !q; if (!q && ch === '(') d++; if (!q && ch === ')') d--; if (!q && d === 0 && ch === ',') { parts.push(cur); cur = ''; } else cur += ch; }
    if (cur) parts.push(cur); return parts;
  }
  const listVals = v => splitTop(v.replace(/^[({]/, '').replace(/[)}]$/, '')).map(x => x.replace(/^"(.*)"$/, '$1'));

  function makeMem(META, DATA, onChange) {
    const T = META.tables, FK = META.fks || [];
    const seq = {};
    for (const t in T) { DATA[t] = DATA[t] || []; const idc = T[t].cols.find(c => c.id); if (idc) seq[t] = DATA[t].reduce((m, r) => Math.max(m, +r[idc.n] || 0), 0); }
    const tbl = n => { if (!T[n]) throw new HttpError(404, `relation "public.${n}" does not exist`, '42P01'); return T[n]; };
    const col = (t, n) => { const c = tbl(t).cols.find(c => c.n === n); if (!c) throw new HttpError(400, `column ${t}.${n} does not exist`, '42703'); return c; };
    const denyPin = (t, n) => { if (t === 'stores' && n === 'pin') throw new HttpError(403, 'permission denied for table stores', '42501'); };

    function coerce(c, v) {
      if (v === null || v === undefined) return null;
      switch (kind(c.t)) {
        case 'int': { const n = Number(v); if (!Number.isFinite(n) || (typeof v === 'string' && v.trim() === '')) throw new HttpError(400, `invalid input syntax for type ${c.t}: "${v}"`, '22P02'); return Math.trunc(n); }
        case 'num': { const n = Number(v); if (!Number.isFinite(n) || (typeof v === 'string' && v.trim() === '')) throw new HttpError(400, `invalid input syntax for type numeric: "${v}"`, '22P02'); return n; }
        case 'bool': return v === true || v === 'true' || v === 't';
        case 'arr': return Array.isArray(v) ? v : (typeof v === 'string' ? listVals(v) : [v]);
        case 'json': return typeof v === 'string' ? (() => { try { return JSON.parse(v); } catch (e) { return v; } })() : v;
        default: return typeof v === 'string' ? v : String(v);
      }
    }
    const today = () => new Date().toISOString().slice(0, 10);
    function defaultOf(t, c) {
      if (c.id) return ++seq[t];
      const d = c.d; if (d == null) return null;
      if (/^now\(\)$/i.test(d)) return new Date().toISOString();
      if (/^CURRENT_DATE$/i.test(d)) return today();
      if (/gen_random_uuid/.test(d)) return (g.crypto && g.crypto.randomUUID) ? g.crypto.randomUUID() : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, ch => { const r = Math.random() * 16 | 0; return (ch === 'x' ? r : (r & 3 | 8)).toString(16); });
      let m;
      if ((m = /^'(.*)'::(?:text|character varying)$/s.exec(d))) return m[1].replace(/''/g, "'");
      if ((m = /^'(.*)'::jsonb?$/s.exec(d))) return JSON.parse(m[1]);
      if (/^'\{\}'::.*\[\]$/.test(d)) return [];
      if ((m = /^'?(-?\d+(?:\.\d+)?)'?(?:::\w+)?$/.exec(d))) return Number(m[1]);
      if (d === 'true') return true; if (d === 'false') return false;
      return null;
    }

    // ----- Filter -----
    const cmpVal = (c, v) => { if (v === null || v === undefined) return null; const k = kind(c.t); return k === 'ts' ? new Date(v).getTime() : (k === 'int' || k === 'num') ? Number(v) : v; };
    function cond(t, name, rest) {
      denyPin(t, name);
      let neg = false; if (rest.startsWith('not.')) { neg = true; rest = rest.slice(4); }
      const i = rest.indexOf('.'), op = rest.slice(0, i), val = rest.slice(i + 1), c = col(t, name), k = kind(c.t); let f;
      const lhs = r => cmpVal(c, r[name]);
      if (op === 'eq') { const v = k === 'bool' ? (val === 'true') : cmpVal(c, val); f = r => lhs(r) !== null && lhs(r) === v; }
      else if (op === 'neq') { const v = cmpVal(c, val); f = r => lhs(r) !== null && lhs(r) !== v; }
      else if (op === 'gt' || op === 'gte' || op === 'lt' || op === 'lte') {
        const v = cmpVal(c, val);
        f = r => { const a = lhs(r); if (a === null) return false; return op === 'gt' ? a > v : op === 'gte' ? a >= v : op === 'lt' ? a < v : a <= v; };
      }
      else if (op === 'like' || op === 'ilike') {
        const re = new RegExp('^' + val.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*|%/g, '.*') + '$', op === 'ilike' ? 'is' : 's');
        f = r => r[name] !== null && r[name] !== undefined && re.test(String(r[name]));
      }
      else if (op === 'is') f = val === 'null' ? (r => r[name] === null || r[name] === undefined) : val === 'true' ? (r => r[name] === true) : val === 'false' ? (r => r[name] === false) : (() => { throw new HttpError(400, 'is: ungültig'); })();
      else if (op === 'in') { const vs = listVals(val).map(x => cmpVal(c, x)); f = r => lhs(r) !== null && vs.includes(lhs(r)); }
      else if (op === 'ov') { const vs = listVals(val).map(String); f = r => Array.isArray(r[name]) && r[name].some(x => vs.includes(String(x))); }
      else throw new HttpError(400, `Operator nicht unterstützt: ${op}`, 'PGRST100');
      return neg ? (r => !f(r)) : f;
    }
    function logic(t, kindName, inner) {
      const fs = splitTop(inner).map(p => { const m = /^(or|and)\((.*)\)$/.exec(p); if (m) return logic(t, m[1], m[2]); const k = p.indexOf('.'); return cond(t, p.slice(0, k), p.slice(k + 1)); });
      return kindName === 'or' ? (r => fs.some(f => f(r))) : (r => fs.every(f => f(r)));
    }
    const RESERVED = new Set(['select', 'order', 'limit', 'offset', 'on_conflict', 'columns']);
    function predicate(t, params) {
      const fs = [];
      for (const [k, v] of params) {
        if (RESERVED.has(k)) continue;
        if (k === 'or' || k === 'and') fs.push(logic(t, k, v.replace(/^\(/, '').replace(/\)$/, ''))); else fs.push(cond(t, k, v));
      }
      return r => fs.every(f => f(r));
    }

    // ----- select / order -----
    const parseSelect = s => splitTop(s).map(p => { const m = /^([A-Za-z0-9_]+)(?:!\w+)?\((.*)\)$/.exec(p); return m ? { emb: m[1], inner: m[2] } : { col: p }; });
    function project(t, row, selStr) {
      const items = parseSelect(selStr || '*'); const out = {};
      for (const it of items) {
        if (it.col !== undefined) {
          if (it.col === '*') { if (t === 'stores') throw new HttpError(403, 'permission denied for table stores', '42501'); Object.assign(out, row); }
          else { col(t, it.col); denyPin(t, it.col); out[it.col] = row[it.col] === undefined ? null : row[it.col]; }
          continue;
        }
        const e = it.emb, one = FK.find(f => f.t === t && f.r === e), many = FK.find(f => f.t === e && f.r === t);
        if (one) { const rel = (DATA[e] || []).find(x => x[one.rc] === row[one.c]); out[e] = rel ? project(e, rel, it.inner) : null; }
        else if (many) out[e] = (DATA[e] || []).filter(x => x[many.c] === row[many.rc]).map(x => project(e, x, it.inner));
        else throw new HttpError(400, `Keine Beziehung zwischen ${t} und ${e}`, 'PGRST200');
      }
      return out;
    }
    function sortRows(t, rows, s) {
      if (!s) return rows;
      const keys = s.split(',').map(p => { const [c, ...mods] = p.split('.'); const cc = col(t, c); const desc = mods.includes('desc'); return { c, cc, desc, nf: mods.includes('nullsfirst') ? true : mods.includes('nullslast') ? false : desc }; });
      return rows.slice().sort((a, b) => {
        for (const k of keys) {
          const x = cmpVal(k.cc, a[k.c]), y = cmpVal(k.cc, b[k.c]);
          if (x === y) continue; if (x === null) return k.nf ? -1 : 1; if (y === null) return k.nf ? 1 : -1;
          const r = x < y ? -1 : 1; return k.desc ? -r : r;
        }
        return 0;
      });
    }

    // ----- Schreiben -----
    function keyOf(row, cols) { return cols.map(c => JSON.stringify(row[c])).join('|'); }
    function uniqueSets(t) { const m = tbl(t); return [...(m.pk ? [m.pk] : []), ...(m.uq || [])]; }
    function findDup(t, row, ignore) {
      for (const set of uniqueSets(t)) {
        if (set.some(c => row[c] === null || row[c] === undefined)) continue;
        const kk = keyOf(row, set); const hit = DATA[t].find(r => r !== ignore && keyOf(r, set) === kk);
        if (hit) return { hit, set };
      }
      return null;
    }
    function buildRow(t, input) {
      const m = tbl(t), row = {};
      for (const c of m.cols) {
        let v = (c.n in input) ? coerce(c, input[c.n]) : undefined;
        if (v === undefined) v = defaultOf(t, c);
        if (v === null && c.nn) throw new HttpError(400, `null value in column "${c.n}" of relation "${t}" violates not-null constraint`, '23502');
        row[c.n] = v;
      }
      for (const k of Object.keys(input)) if (!m.cols.some(c => c.n === k)) throw new HttpError(400, `Could not find the '${k}' column of '${t}' in the schema cache`, 'PGRST204');
      return row;
    }
    const dupErr = (t, set) => new HttpError(409, `duplicate key value violates unique constraint "${t}_${set.join('_')}_key"`, '23505');

    function table(req, name, pref) {
      const m = req.method, params = req.params; tbl(name);
      const ret = pref.return === 'representation';
      if (m === 'GET' || m === 'HEAD') {
        const pred = predicate(name, params);
        let rows = sortRows(name, DATA[name].filter(pred), params.get('order'));
        let lim = params.get('limit'), off = params.get('offset'); const rg = req.headers.range; let ranged = false;
        if (rg && /^\d+-\d*$/.test(rg)) { const [a, b] = rg.split('-'); ranged = true; off = a; if (b !== '') lim = String(+b - +a + 1); }
        const o = +off || 0; rows = rows.slice(o, lim ? o + (+lim | 0) : undefined);
        const out = rows.map(r => project(name, r, params.get('select')));
        return R(ranged && out.length ? 206 : 200, m === 'HEAD' ? '' : out, (ranged || lim) ? { 'Content-Range': out.length ? `${o}-${o + out.length - 1}/*` : '*/*' } : {});
      }
      const body = req.body ? JSON.parse(req.body) : null;
      if (m === 'POST') {
        const rows = Array.isArray(body) ? body : [body]; const result = [];
        const rs = pref.resolution, oc = params.get('on_conflict');
        const target = oc ? oc.split(',') : (tbl(name).pk || []);
        const staged = []; // erst alles prüfen, dann übernehmen (atomar wie bei Postgres)
        const work = DATA[name].slice();
        const snapshotSeq = seq[name];
        try {
          for (const input of rows) {
            const row = buildRow(name, input);
            if (rs === 'merge-duplicates' || rs === 'ignore-duplicates' || oc) {
              const hit = work.find(r => keyOf(r, target) === keyOf(row, target));
              if (hit) {
                if (rs === 'ignore-duplicates') continue;
                for (const k of Object.keys(input)) if (!target.includes(k)) hit[k] = row[k];
                result.push(hit); continue;
              }
            }
            const dup = (() => { for (const set of uniqueSets(name)) { if (set.some(c => row[c] == null)) continue; const kk = keyOf(row, set); if (work.some(r => keyOf(r, set) === kk)) return set; } return null; })();
            if (dup) throw dupErr(name, dup);
            work.push(row); staged.push(row); result.push(row);
          }
        } catch (e) { seq[name] = snapshotSeq; throw e; }
        DATA[name] = work; onChange && onChange();
        return R(201, ret ? result.map(r => ({ ...r })) : '');
      }
      if (m === 'PATCH') {
        const pred = predicate(name, params), upd = []; const cols = Object.keys(body || {});
        if (!cols.length) return R(204);
        for (const r of DATA[name]) if (pred(r)) {
          const next = { ...r };
          for (const c of cols) { const cc = col(name, c); const v = coerce(cc, body[c]); if (v === null && cc.nn) throw new HttpError(400, `null value in column "${c}" of relation "${name}" violates not-null constraint`, '23502'); next[c] = v; }
          const dup = findDup(name, next, r); if (dup) throw dupErr(name, dup.set);
          upd.push([r, next]);
        }
        for (const [r, next] of upd) Object.assign(r, next);
        onChange && onChange();
        return ret ? R(200, upd.map(([r]) => ({ ...r }))) : R(204);
      }
      if (m === 'DELETE') {
        if (![...params.keys()].some(k => !RESERVED.has(k))) throw new HttpError(400, 'DELETE ohne Filter nicht erlaubt', 'PGRST');
        const pred = predicate(name, params); const del = DATA[name].filter(pred);
        DATA[name] = DATA[name].filter(r => !pred(r)); onChange && onChange();
        return ret ? R(200, del) : R(204);
      }
      throw new HttpError(405, 'Methode nicht unterstützt');
    }

    function rpc(req, fn) {
      const args = req.method === 'POST' && req.body ? JSON.parse(req.body) : Object.fromEntries(req.params);
      if (fn === 'check_store_pin') {
        const s = DATA.stores.find(x => x.id === args.p_store_id && x.pin === args.p_pin);
        return R(200, s ? [{ id: s.id, name: s.name }] : []);
      }
      throw new HttpError(404, `Funktion ${fn} gibt es im Offline-Testmodus nicht`, 'PGRST202');
    }

    function handle(req) {
      try {
        const path = req.path; let mm;
        const prefer = Object.fromEntries((req.headers.prefer || '').split(',').map(x => x.trim()).filter(Boolean).map(x => x.split('=')));
        if ((mm = /^\/rest\/v1\/rpc\/([^/]+)$/.exec(path))) return rpc(req, mm[1]);
        if ((mm = /^\/rest\/v1\/([^/]+)$/.exec(path))) return table(req, decodeURIComponent(mm[1]), prefer);
        if (/^\/(functions|storage|auth)\/v1\//.test(path)) return R(501, { message: 'Im Testmodus nicht verfügbar: ' + path.split('/')[1] });
        return R(404, { message: 'Not found' });
      } catch (e) {
        if (e instanceof HttpError) return R(e.status, { message: e.message, code: e.code || 'PGRST', details: null, hint: null });
        return R(500, { message: String(e && e.message || e) });
      }
    }
    return { handle, DATA };
  }
  const api = { makeMem };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else g.KarmaMem = api;
})(typeof window !== 'undefined' ? window : globalThis);
