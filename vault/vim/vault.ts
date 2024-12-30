import { HomeLayout, ResLayout } from "@dotfiles/lib/layout.ts";
import { Result } from "@dotfiles/lib/lang.ts";
import { CookBook, PrefSpec, TmplSpec } from "@dotfiles/lib/schema.ts";
import * as theme from "@dotfiles/lib/theme.ts";
import * as shell from "@dotfiles/lib/shell.ts";

export const VimCookBook = new CookBook({
  name: "VimCookBook",
  container: ResLayout.vault().join("vim/"),
  prefs: [
    new PrefSpec({
      src: ".",
      dst: HomeLayout.config().join("vim/"),
    }),
  ],
  tmpls: [
    new TmplSpec({
      src: "vimrc",
      dst: "~/.vimrc",
    }),
  ],
  setup: async (options: shell.CallOptions) => {
    const highlights = [
      {
        "name": "SpecialKey",
        "foreground": 4,
        "options": ["bold"],
      },
      {
        "name": "NonText",
        "foreground": 12,
        "options": ["bold"],
      },
      {
        "name": "Directory",
        "foreground": 4,
        "options": ["bold"],
      },
      {
        "name": "ErrorMsg",
        "foreground": 15,
        "background": 1,
        "options": ["standout"],
      },
      {
         "name": "IncSearch",
          "options": ["reverse"],
      },
      {
        "name": "Search",
        "background": 11,
        "options": ["reverse"],
      },
      {
        "name": "MoreMsg",
        "foreground": 2,
        "options": ["bold"],
      },
      {
        "name": "ModeMsg",
        "options": ["bold"],
      },
      {
        "name": "LineNr",
        "foreground": 130,
      },
      {
          "name": "CursorLineNr",
          "foreground": 130,
          "options": ["bold"],
      },
      {
        "name": "Question",
        "foreground": 2,
        "options": ["standout"],
      },
      {
        "name": "StatusLine",
        "options": ["bold", "reverse"],
      },
      {
        "name": "StatusLineNC",
        "options": ["reverse"],
      },
      {
        "name": "VertSplit",
        "options": ["reverse"],
      },
      {
        "name": "Title",
        "foreground": 5,
        "options": ["bold"],
      },
      {
        "name": "Visual",
        "background": 7,
        "options": ["reverse"],
      },
      {
        "name": "VisualNOS",
        "options": ["bold", "underline"],
      },
      {
        "name": "WarningMsg",
        "foreground": 1,
        "options": ["standout"],
      },
      {
        "name": "WildMenu",
        "foreground": 0,
        "background": 11,
        "options": ["standout"],
      },
      {
        "name": "Folded",
        "foreground": 0,
        "background": 15,
        "options": ["standout"],
      },
      {
        "name": "FoldColumn",
        "foreground": 0,
        "background": 15,
        "options": ["standout"],
      },
      {
        "name": "DiffAdd",
        "foreground": 0,
        "background": 2,
        "options": ["bold"],
      },
      {
        "name": "DiffChange",
        "foreground": 0,
        "background": 3,
        "options": ["bold"],
      },
      {
        "name": "DiffDelete",
        "foreground": 0,
        "background": 6,
        "options": ["bold"],
      },
      {
        "name": "DiffText",
        "foreground": 0,
        "background": 7,
        "options": ["reverse", "bold"],
      },
      {
        "name": "SignColumn",
        "background": 0,
        "options": ["NONE"],
      },
      {
        "name": "Conceal",
        "foreground": 7,
        "background": 242,
      },
      {
        "name": "SpellBad",
        "background": 224,
        "options": ["reverse"],
      },
      {
        "name": "SpellCap",
        "background": 81,
        "options": ["reverse"],
      },
      {
        "name": "SpellRare",
        "background": 225,
        "options": ["reverse"],
      },
      {
        "name": "SpellLocal",
        "background": 14,
      },
      {
        "name": "Pmenu",
        "foreground": 0,
        "background": 225,
      },
      {
        "name": "PmenuSel",
        "foreground": 0,
        "background": 248,
      },
      {
        "name": "PmenuSbar",
        "background": 248,
      },
      {
        "name": "PmenuThumb",
        "background": 0,
      },
      {
        "name": "TabLine",
        "foreground": 0,
        "background": 7,
        "options": ["underline"],
      },
      {
        "name": "TabLineSel",
        "options": ["bold"],
      },
      {
        "name": "TabLineFill",
        "options": ["reverse"],
      },
      {
        "name": "CursorColumn",
        "background": 7,
      },
      {
        "name": "CursorLine",
        "options": ["underline"],
      },
      {
        "name": "ColorColumn",
        "background": 224,
        "options": ["reverse"],
      },
      {
        "name": "MatchParen",
        "foreground": 0,
        "background": 7,
        "options": ["reverse"],
      },
      {
        "name": "Comment",
        "foreground": 4,
        "options": ["bold"],
      },
      {
        "name": "Constant",
        "foreground": 1,
      },
      {
        "name": "Special",
        "foreground": 5,
        "options": ["bold"],
      },
      {
        "name": "Identifier",
        "foreground": 6,
      },
      {
        "name": "Statement",
        "foreground": 130,
        "options": ["bold"],
      },
      {
        "name": "PreProc",
        "foreground": 5,
      },
      {
        "name": "Type",
        "foreground": 2,
      },
      {
        "name": "Underlined",
        "foreground": 5,
        "options": ["underline"],
      },
      {
        "name": "Ignore",
        "foreground": 15,
      },
      {
        "name": "Error",
        "foreground": 15,
        "background": 9,
        "options": ["reverse"],
      },
      {
        "name": "Todo",
        "foreground": 0,
        "background": 11,
        "options": ["standout"],
      },
    ];

    const aliases = [
      {
        "name": "Character",
        "link": "Constant",
      },
      {
        "name": "Number",
        "link": "Constant",
      },
      {
        "name": "Boolean",
        "link": "Constant",
      },
      {
        "name": "Float",
        "link": "Number",
      },
      {
        "name": "Function",
        "link": "Identifier",
      },
      {
        "name": "Conditional",
        "link": "Statement",
      },
      {
        "name": "Repeat",
        "link": "Statement",
      },
      {
        "name": "Label",
        "link": "Statement",
      },
      {
        "name": "Operator",
        "link": "Statement",
      },
      {
        "name": "Keyword",
        "link": "Statement",
      },
      {
        "name": "Exception",
        "link": "Statement",
      },
      {
        "name": "Include",
        "link": "PreProc",
      },
      {
        "name": "Define",
        "link": "PreProc",
      },
      {
        "name": "Macro",
        "link": "PreProc",
      },
      {
        "name": "PreCondit",
        "link": "PreProc",
      },
      {
        "name": "StorageClass",
        "link": "Type",
      },
      {
        "name": "Structure",
        "link": "Type",
      },
      {
        "name": "Typedef",
        "link": "Type",
      },
      {
        "name": "Tag",
        "link": "Special",
      },
      {
        "name": "SpecialChar",
        "link": "Special",
      },
      {
        "name": "Delimiter",
        "link": "Special",
      },
      {
        "name": "SpecialComment",
        "link": "Special",
      },
      {
        "name": "Debug",
        "link": "Special",
      },
    ];

    const lines = [`let g:colors_name="muniere"`, ""];
    const palette = theme.Palette;

    for (const highlight of highlights) {
      const chunks = ["highlight", highlight.name];

      if (highlight.foreground !== undefined) {
        chunks.push(`ctermfg=${highlight.foreground}`);

        const color = palette[highlight.foreground];
        if (color !== undefined) {
          chunks.push(`guifg=${color}`);
        }
      }
      if (highlight.background !== undefined) {
        chunks.push(`ctermbg=${highlight.background}`);

        const color = palette[highlight.background];
        if (color !== undefined) {
          chunks.push(`guibg=${color}`);
        }
      }
      if (highlight.options) {
        chunks.push(`term=${highlight.options.join(",")}`);
        chunks.push(`cterm=${highlight.options.join(",")}`);
        chunks.push(`gui=${highlight.options.join(",")}`);
      }

      lines.push(chunks.join(" "));
    }

    for (const alias of aliases) {
      const chunks = ["highlight", "link", alias.name, alias.link];

      lines.push(chunks.join(" "));
    }

    const content = lines.join("\n");
    const dst = ResLayout.vault().join("vim", "default", "colors", "muniere.vim");

    options.logger?.debug(
      `Create a file ${dst} with content:\n${content}`,
    );

    if (options.dryRun == true) {
      return;
    }

    await Deno.writeTextFile(dst.toFileUrl(), content + "\n");
  },
  activate: async (options: shell.CallOptions) => {
    const url = "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim";
    const path = HomeLayout.config().join("vim/autoload/plug.vim");

    const stat = await Result.runAsyncOr(() => path.stat());
    if (stat) {
      options.logger?.info(`File already exists: ${path}`);
      return;
    }

    await shell.curl(url, { ...options, output: path });
  },
});
