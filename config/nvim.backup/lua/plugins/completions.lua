local gh = require('plugin_utils')

-- Snippet engine + autocompletion engine, installed together.
vim.pack.add({
  { src = gh('L3MON4D3/LuaSnip'), version = vim.version.range('2.*') },
  { src = gh('saghen/blink.cmp'), version = vim.version.range('1.*') },
})

require('luasnip').setup()

require('blink.cmp').setup({
  snippets = { preset = 'luasnip' },

  sources = {
    -- Order settles ties: your own snippets first, then real LSP
    -- completions (Typst std lib, C std headers, ...), then path, and
    -- buffer-text guesses last (see score_offset below).
    default = { 'snippets', 'lsp', 'path', 'buffer' },
    providers = {
      -- Buffer-text matches rank behind everything else — only useful
      -- as a fallback when nothing "smart" has a suggestion.
      buffer = {
        score_offset = -3,
      },
    },
  },

  -- preset = 'none': blink's own 'default' preset binds <Tab>/<S-Tab> for
  -- menu navigation, which collides with the smart-tab logic in
  -- keymaps.lua. Keeping this Tab-free means keymaps.lua owns Tab
  -- entirely, and the menu is only driven by these explicit keys.
  keymap = {
    preset = 'none',
    ['<C-space>'] = { 'select_and_accept', 'show' },
    ['<C-n>'] = { 'select_next', 'fallback' },
    ['<C-p>'] = { 'select_prev', 'fallback' },
    ['<C-e>'] = { 'hide', 'fallback' },
  },
})
