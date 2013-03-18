AceJump
=======

Plug-in for Sublime Text 2 and Sublime Text 3

It's inspired by AceJump for JetBrains WebStorm (inspired by emacs AceJump, which is inspired by EasyMotion for Vim)

Possibilities
------------

With just one keyboard shortcut and two typed letters you can set your cursor to the beginning or end of any word (or text chunk) on the screen.

Description
---------------------------

After you type a keyboard shortcut (default is `ctrl+;`) an input field is opened. First character you type launches function which searches for all text chunks containing this character. Then it labels all found occurrences. Next letter(s) you type are interpreted as label you want jump to. If you then press enter the cursor will be before your label.

Notice that current plug-in status is indicated in status bar.

How to use it
-------------

Input: `<first_character_in_word><searching_word_label>`

- Press keyboard shortcut to activate plug-in.
- Type character to search for.
- Type label letter(s) corresponding to your word and press enter

Keyboard Shortcuts:
- `ctrl+;`          - place cursor at the beginning of the word
- `ctrl+shift+;`    - pace cursor at the end of the word
- `ctrl+alt+;`      - selects the word
- `ctrl+alt+g+;`    - selects all matching words

How to install
--------------

Just put AceJump folder to Packages directory of ST2 or ST3
(Preferences > Browse Packages)

Thoughts
--------

I did it that way, because that's all I found about Sublime Text 2 API.
I used
- Window.show_input_panel to collect user input
- View.replace, View.add_regions and command undo to implement labels
- similar mechanism to goto_line.py to jump

tl;dr
-----

Press `ctrl+;`, type first character, letter, `<enter>`, profit.
