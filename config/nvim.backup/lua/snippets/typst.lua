-- Typst snippets. See lua/plugins/snippets.lua for how this file is loaded.
local ls = require('luasnip')
local s, t, i = ls.snippet, ls.text_node, ls.insert_node

return {
  -- Expand instantly as you type the trigger — no <Tab> needed.
  autosnippets = {
    s({ trig = 'mk' }, {
      t('$'), i(1), t('$ '), i(2),
    }),

    -- t() nodes can't contain a literal \n — a table of strings is how
    -- LuaSnip represents a line break (each entry is one line).
    s({ trig = 'dm' }, {
      t({ '$', '  ' }), i(1), t({ '', '$' }), i(2),
    }),
  },

  -- Expand via <Tab> or the completion menu.
  snippets = {
    s('frac', {
      t('frac('), i(1), t(', '), i(2), t(') '), i(3),
    }),
  },
}
