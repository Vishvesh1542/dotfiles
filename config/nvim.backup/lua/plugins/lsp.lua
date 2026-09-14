local gh = require('plugin_utils')

-- Install everything in one call (one dependency resolution pass instead
-- of six) — setup order below still matches how they used to load.
vim.pack.add({
  gh('NMAC427/guess-indent.nvim'),
  gh('lewis6991/gitsigns.nvim'),
  gh('folke/which-key.nvim'),
  gh('rebelot/kanagawa.nvim'),
  gh('folke/todo-comments.nvim'),
  gh('nvim-mini/mini.nvim'),
})

-- ============================================================
-- INDENTATION / GIT / KEYBIND HINTS
-- ============================================================
require('guess-indent').setup()

require('gitsigns').setup({
  signs = {
    add = { text = '+' },
    change = { text = '~' },
    delete = { text = '_' },
    topdelete = { text = '‾' },
    changedelete = { text = '~' },
  },
})

require('which-key').setup({
  delay = 0,
  icons = {
    mappings = vim.g.have_nerd_font,
  },
  spec = {
    { '<leader>s', group = '[S]earch', mode = { 'n', 'v' } },
    { '<leader>t', group = '[T]oggle' },
    { '<leader>h', group = 'Git [H]unk', mode = { 'n', 'v' } },
    { 'gr', group = 'LSP Actions', mode = { 'n' } },
  },
})

-- ============================================================
-- COLORSCHEME
-- ============================================================
require('kanagawa').setup({
  compile = true,
  undercurl = true,
  commentStyle = { italic = true },
  functionStyle = {},
  keywordStyle = { italic = true },
  statementStyle = { bold = true },
  typeStyle = {},
  transparent = false,
  dimInactive = true,
  terminalColors = true,
  colors = {
    palette = {},
    theme = { wave = {}, lotus = {}, dragon = {}, all = {} },
  },
  overrides = function(_colors)
    return {}
  end,
  theme = 'dragon',
  background = {
    dark = 'dragon',
    light = 'lotus',
  },
})
vim.cmd.colorscheme('kanagawa')

require('todo-comments').setup({
  signs = false,
})

-- ============================================================
-- MINI.NVIM
-- ============================================================

-- Auto-close (), [], {}, "", '', ``, ** on typing the opener. `neigh_pattern`
-- is matched against the 2-char neighborhood (char before + after cursor),
-- so patterns here must match exactly 2 characters.
require('mini.pairs').setup({
  mappings = {
    ['('] = { action = 'open', pair = '()', neigh_pattern = '[^\\].' },
    ['['] = { action = 'open', pair = '[]', neigh_pattern = '[^\\].' },
    ['{'] = { action = 'open', pair = '{}', neigh_pattern = '[^\\].' },

    -- 'open' (not 'closeopen'/'close'): auto-inserts the pair, but never
    -- skips over an existing matching character instead of inserting a
    -- new one — Tab is what jumps past closers, not typing them again.
    ['"'] = { action = 'open', pair = '""', neigh_pattern = '[^\\].' },
    ["'"] = { action = 'open', pair = "''", neigh_pattern = '[^%a\\].' },
    ['`'] = { action = 'open', pair = '``', neigh_pattern = '[^\\].' },
    ['*'] = { action = 'open', pair = '**', neigh_pattern = '[^\\].' },
  },
})

-- setup() merges into mini.pairs' own defaults rather than replacing
-- them, so ), ], } would otherwise keep their default "skip over an
-- existing one" behavior. Remap them back to plain, literal insertion.
vim.keymap.set('i', ')', ')')
vim.keymap.set('i', ']', ']')
vim.keymap.set('i', '}', '}')

if vim.g.have_nerd_font then
  require('mini.icons').setup()
  -- Lets plugins that expect nvim-web-devicons (e.g. Telescope) work with mini.icons.
  MiniIcons.mock_nvim_web_devicons()
end

-- Better around/inside text objects (e.g. `dab`, `ci"`).
require('mini.ai').setup({
  mappings = {
    around_next = 'aa',
    inside_next = 'ii',
  },
  n_lines = 500,
})

-- Add/delete/replace surrounding brackets, quotes, etc.
require('mini.surround').setup()

-- Statusline.
local statusline = require('mini.statusline')
statusline.setup({
  use_icons = vim.g.have_nerd_font,
})
statusline.section_location = function()
  return '%2l:%-2v'
end
