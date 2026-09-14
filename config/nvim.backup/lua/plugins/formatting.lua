local gh = require('plugin_utils')

vim.pack.add({ gh('stevearc/conform.nvim') })

require('conform').setup({
  notify_on_error = false,

  -- Add filetypes here (e.g. lua = true) to format them automatically on save.
  format_on_save = function(bufnr)
    local enabled_filetypes = {}

    if enabled_filetypes[vim.bo[bufnr].filetype] then
      return {
        timeout_ms = 500,
      }
    end
  end,

  default_format_opts = {
    lsp_format = 'fallback',
  },

  -- Add external formatters per filetype here, e.g. lua = { 'stylua' }.
  formatters_by_ft = {},
})
