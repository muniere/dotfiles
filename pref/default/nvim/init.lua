--
-- Functions
--

function vim.api.nvim_has_runtime_path(path)
  for _, x in ipairs(vim.api.nvim_list_runtime_paths()) do
    if x == path then
      return true
    end
  end
  return false
end

--
-- Config
-- 

-- This file's encoding is utf-8
vim.opt.encoding = "utf-8"

-- Default encoding is utf-8
vim.opt.fileencoding = "utf-8"

-- Enable show other buffers without saving current buffer
vim.opt.hidden = true 

-- Enable commandline completion
vim.opt.wildmenu = true

-- Show command at the bottom
vim.opt.showcmd = true

-- Hilight search result
vim.opt.hlsearch = true

-- Backup
vim.opt.backupskip = { "/tmp/*", "/private/tmp/*" }

-- Do not show preview window when completion
vim.opt.completeopt:remove { "preview" }

-- Ignore whitespace diff
vim.opt.diffopt:append { "iwhite" }

-- Ignore capital case and small case when text search
vim.opt.ignorecase = true
vim.opt.smartcase = true

-- Enable backspace key
vim.opt.backspace = { "indent", "eol", "start" }

-- Enable autoindent
vim.opt.autoindent = true 

-- Do not move to start of line when move to other line
vim.opt.startofline = false

-- Show ruler at the bottom
vim.opt.ruler = true

-- Always show staus line
vim.opt.laststatus = 2

-- Confirm save or not if buffer has changed
vim.opt.confirm = true 

-- Use visual bell instead of beap
vim.opt.visualbell = true 

-- Enable mouse 
vim.opt.mouse = "a"

-- Set command line height
vim.opt.cmdheight = 1

-- Show line number
vim.opt.number = true

-- Set timeout length of keycode
vim.opt.timeout = false
vim.opt.ttimeout = false
vim.opt.ttimeoutlen = 200

-- Turn off IME when switch to insert mode
vim.opt.iminsert = 0
vim.opt.imsearch = 0

-- Set fold method to marker
vim.opt.foldmethod = "marker"

-- Enable modeline
vim.opt.modeline = true
vim.opt.modelines = 5

-- Use 4 spaces in place of tab
vim.opt.shiftwidth = 4
vim.opt.softtabstop = 4
vim.opt.tabstop = 4
vim.opt.expandtab = true 

-- Set new window directions
vim.opt.splitbelow = true
vim.opt.splitright = true

-- Shell script with bash mode
vim.g["is_bash"] = true

-- Move to last edit position
vim.api.nvim_create_autocmd("BufReadPost", {
  pattern = "*",
  callback = function () 
    if vim.fn.line("'\"") > 0 and vim.fn.line("'\"") <= vim.fn.line("$") then
     vim.cmd("normal g'\"")
    end
  end
})

-- Do not continue comment line
vim.api.nvim_create_autocmd("FileType", {
  pattern = "*",
  callback = function () 
    vim.opt.formatoptions:remove { "r", "o" }
  end,
})

--
-- Keymaps
-- 

-- Move in visual line
vim.keymap.set("n", "j", "gk")
vim.keymap.set("n", "j", "gj")

--
-- Plugins
--
local plug = {
  begin = vim.fn["plug#begin"],
  end_ = vim.fn["plug#end"],
  call = vim.fn["plug#"],
  sync = function ()
    vim.cmd("PlugInstall --sync")
  end,
  miss = function ()
    local plugs = vim.g["plugs"]
    local count = 0

    for _, plug in pairs(plugs) do
      local file = io.open(plug.dir, "r")

      if file == nil then
        count = count + 1
      else
        file:close()
      end
    end

    return count
  end,
  test = function (name) 
    local plugs = vim.g["plugs"]

    local plug = plugs[name]
    if plug == nil then
      return false
    end

    local dir = plug["dir"]
    if dir == nil then
      return false
    end

    local path = string.gsub(dir, [[/+$]], "")

    local file = io.open(path, "r")
    if file == nil then
      return false
    end

    file:close()

    return vim.api.nvim_has_runtime_path(path)
  end
}

plug.begin(vim.env.XDG_DATA_HOME .. "/nvim/plugged")

plug.call("tomasr/molokai")

plug.call("vim-scripts/sudo.vim")
plug.call("vim-scripts/surround.vim")
plug.call("editorconfig/editorconfig-vim")

plug.call("itchyny/lightline.vim")
plug.call("lambdalisue/nerdfont.vim")

plug.call("lambdalisue/fern.vim")
plug.call("lambdalisue/fern-renderer-nerdfont.vim")

plug.call("junegunn/fzf", { ["do"] = vim.fn["fzf#install"] })
plug.call("junegunn/fzf.vim")

plug.call("vim-denops/denops.vim")
plug.call("Shougo/ddc.vim")
plug.call("Shougo/ddc-around")
plug.call("Shougo/ddc-matcher_head")
plug.call("Shougo/ddc-sorter_rank")
plug.call("Shougo/ddc-ui-native")

plug.end_()

vim.api.nvim_create_autocmd("VimEnter", {
  pattern = "*",
  callback = function ()
    if plug.miss() > 0 then
      plug.sync()
    end
  end,
})

-- lightline
if plug.test("lightline.vim") then
  vim.g["lightline"] = {
    active  = { 
      left = { {"mode"}, {"relativepath"}, {"modified"} } 
    },
    inactive = {
      left = { {"mode"}, {"relativepath"}, {"modified"} }
    }
  }
end

-- fern 
if plug.test("fern.vim") then
  vim.g["fern#renderer"] = "nerdfont"
  vim.g["fern#default_hidden"] = true

  vim.keymap.set("n", "<C-e><C-e>", ":Fern . -drawer -toggle<CR>", { noremap = true, silent = true })
  vim.keymap.set("i", "<ESC><C-e><C-e>", ":Fern . -drawer -toggle <CR>", { noremap = true, silent = true })
  vim.keymap.set("n", "<C-e><C-f>", ":Fern . -drawer -toggle -reveal=%<CR>", { noremap = true, silent = true })
  vim.keymap.set("i", "<ESC><C-e><C-f>", ":Fern . -drawer -toggle -reveal=%<CR>", { noremap = true, silent = true })

  vim.api.nvim_create_autocmd("FileType", {
    pattern = "fern",
    callback = function () 
      vim.opt_local.number = false
      vim.opt_local.relativenumber = false
      vim.keymap.set("n", "<Plug>(fern-action-open-or-enter)", "<Plug>(fern-action-open-or-expand)", { buffer = true })
    end,
  })
end

-- fzf
if plug.test("fzf.vim") then
  vim.g["fzf_preview_window"] = {}

  vim.keymap.set("n", "<C-x><C-f>", ":Files<CR>", { noremap = true, silent = true })
  vim.keymap.set("i", "<C-x><C-f>", "<ESC>:Files<CR>", { noremap = true, silent = true })
  vim.keymap.set("n", "<C-x><C-b>", ":Buffers<CR>", { noremap = true, silent = true })
  vim.keymap.set("i", "<C-x><C-b>", "<ESC>:Buffers<CR>", { noremap = true, silent = true })
end


-- ddc
if plug.test("ddc.vim") then
  local ddc = {
    custom = {
      patch_global = vim.fn["ddc#custom#patch_global"]
    },
    enable = vim.fn["ddc#enable"],
  }

  ddc.custom.patch_global("ui", "native")
  ddc.custom.patch_global("sources", { "around" })
  ddc.custom.patch_global("sourceOptions", {
    _ = {
      matchers = { "matcher_head" },
      sorters = { "sorter_rank" },
    }
  })

  vim.keymap.set('i', '<Tab>', function()
    return vim.fn.pumvisible() == 1 and '<Space>' or '<Tab>'
  end, { expr = true })

  ddc.enable()
end


--
-- Appearance
--

if plug.test("molokai") then
  vim.cmd("colorscheme molokai")
end

-- vim: ft=lua ts=2 sts=2 sw=2
