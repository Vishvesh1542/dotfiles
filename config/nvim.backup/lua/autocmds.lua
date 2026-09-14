local yank_group = vim.api.nvim_create_augroup('highlight-yank', {
  clear = true,
})

vim.api.nvim_create_autocmd('TextYankPost', {
  group = yank_group,
  desc = 'Highlight when yanking',
  callback = function()
    vim.hl.on_yank()
  end,
})
