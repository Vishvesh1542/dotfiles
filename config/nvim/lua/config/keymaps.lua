-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

local close_chars = {
  [")"] = true,
  ["]"] = true,
  ["}"] = true,
  ['"'] = true,
  ["'"] = true,
  ["`"] = true,
  ["*"] = true,
  ["/"] = true,
  [">"] = true,
}

vim.keymap.set("i", "<Tab>", function()
  -- let blink.cmp's menu navigation win if it's open
  local ok, blink = pcall(require, "blink.cmp")
  if ok and blink.is_visible and blink.is_visible() then
    return "<C-n>" -- or whatever you use to move to next item
  end

  local line = vim.api.nvim_get_current_line()
  local row, col = unpack(vim.api.nvim_win_get_cursor(0))
  local i = col + 1
  while line:sub(i, i) == " " do
    i = i + 1
  end
  local ch = line:sub(i, i)

  if close_chars[ch] then
    vim.api.nvim_win_set_cursor(0, { row, i }) -- jump just past this one char
  else
    vim.api.nvim_feedkeys(vim.api.nvim_replace_termcodes("<Tab>", true, false, true), "n", false)
  end
end, { desc = "Skip over closing char or insert tab" })
