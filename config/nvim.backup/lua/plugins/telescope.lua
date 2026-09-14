local gh = require('plugin_utils')

-- ============================================================
-- INSTALL
-- ============================================================
local plugins = {
  gh('nvim-lua/plenary.nvim'),
  gh('nvim-telescope/telescope.nvim'),
  gh('nvim-telescope/telescope-ui-select.nvim'),
}

-- The native fzf sorter needs a C compiler to build, so only install it
-- when `make` is available.
if vim.fn.executable('make') == 1 then
  table.insert(plugins, gh('nvim-telescope/telescope-fzf-native.nvim'))
end

vim.pack.add(plugins)

-- ============================================================
-- SETUP
-- (Keymaps that use `require('telescope.builtin')` live in keymaps.lua.)
-- ============================================================
local telescope = require('telescope')

telescope.setup({
  extensions = {
    ['ui-select'] = {
      require('telescope.themes').get_dropdown(),
    },
  },
})

pcall(telescope.load_extension, 'fzf')
pcall(telescope.load_extension, 'ui-select')
