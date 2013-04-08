import sublime
import sublime_plugin
from string import ascii_uppercase
from re import search, match, escape


hints_letters = ascii_uppercase
hints_letters_length = len(hints_letters)


def number_to_letters(number):
	# Like in excel columns
	base = hints_letters_length
	string = ""
	while number:
		m = (number - 1) % base
		string += hints_letters[m]
		number = int((number - m) / base)
	return string[::-1]


def letters_to_number(string):
	string = string[::-1]
	base = hints_letters_length
	quantity = len(string)
	number = 0
	for i in range(quantity):
		number += (int(string[i], 36) - 9) * pow(base, i)
	return number

# Will contain all words matched to selection_regex % self.char
SublimeJump_WORDS = []
# Tells if labels are shown
SublimeJump_HAS_LABELS = False


'''
What are we gonna do here? (function activated)
	get first character
	search all words in the current view starting with this letter and label them
	jump to selected word (and select if modifier activated)
'''


class SublimeJumpCommand(sublime_plugin.TextCommand):

	def run(self, edit, key_modifier):
		self.key_modifier = key_modifier
		self.settings = sublime.load_settings('SublimeJump.sublime-settings')
		# Some base variables
		# Reference to current view
		self.view = self.view.window().active_view()

		# Character we are looking for
		self.char = ""
		# Target label (and modifier)
		self.target = ""

		# Edit object for labels
		self.edit = edit
		self.view.set_status("SublimeJump", "Search for character")
		# Is there a moar awesome way?

		self.view.window().show_input_panel(
			"SublimeJump prompt", "",
			self.input, self.change, self.nope
		)
		# We could use overlay as well, but it can cover some words

	def input(self, command):
		# Got user input, disable labels and jump
		self.nope()
		self.jump()

	def change(self, command):
		global SublimeJump_HAS_LABELS

		if not command:
			# If user entered text, deleted it and started over

			if SublimeJump_HAS_LABELS:
				self.unlabel_words()

			self.view.set_status("SublimeJump", "Type target character")
			return

		if len(command) == 1:
			# Just first character
			self.char = command

			if not SublimeJump_HAS_LABELS:
				self.search_and_label_words()

		if len(command) > 1:
			# Label (and modifier)
			self.target = command[1:]
			self.view.set_status("SublimeJump", "Target: %s" % self.target)

	def nope(self):
		# User canceled input
		#if SublimeJump_HAS_LABELS:
		self.unlabel_words()
		self.view.erase_status("SublimeJump")
		# if caller != input:
		sublime.status_message("SublimeJump: Canceled")

	def search_and_label_words(self):
		self.view.run_command('add_hint',
			{
				"char": self.char,
				"selection_regex": self.settings.get('jump_regex'),
				"highlight_match": self.settings.get('highlight_match')
			}
		)

	def unlabel_words(self):
		global SublimeJump_HAS_LABELS
		# Erase hints and undo labels in the fine
		SublimeJump_HAS_LABELS = False
		self.view.erase_regions("SublimeJumpHints")
		self.view.erase_regions("SublimeJumpWords")
		#self.view.end_edit(self.edit)
		self.view.run_command("undo")

	def jump(self):
		global SublimeJump_WORDS
		# Todo: Last jump position, so you can jump back with one letter shortcut
		# Todo: Settings: add default jump mode
		# Todo: Add select_to modifier
		# Get label and modifier
		result = search(r'(\w+)(.?)', self.target)

		if result:
			label = result.group(1).lower()
			modifier = result.group(2)
		else:
			sublime.status_message("Bad input!")
			return

		# Convert label to number, and get its region
		index = letters_to_number(label) - 1
		region = SublimeJump_WORDS[index]

		if self.key_modifier == 'jump_to_word_end':
			# End of word
			self.view.run_command("jump_to_place", {"start": region.end()})
			return

		if self.key_modifier == 'select_word':
			# Select word
			self.view.run_command("jump_to_region", {"start": region.begin(), "end": region.end()})
			return

		if self.key_modifier == 'select_all_words':
			# Select word
			self.view.run_command("jump_to_regions", {"start": region.begin(), "end": region.end()})
			return

		sublime.status_message(
			"Search key: %s, go to: %s%s"
			% (self.char, label, "" if not modifier else ", no such modifier, just jumping")
		)
		self.view.run_command("jump_to_place", {"start": region.begin()})


class AddHintCommand(sublime_plugin.TextCommand):
	def run(self, edit, char, selection_regex, highlight_match):
		global SublimeJump_WORDS, SublimeJump_HAS_LABELS
		# http://www.sublimetext.com/docs/2/api_reference.html
		# http://docs.python.org/2/library/re.html
		# Todo: One letter labels closer to current position
		# Searches for all words with given regexp in current view and labels them
		# Contain words regions, so we can use entire region, or just one position
		hints = []

		self.view = self.view.window().active_view()
		self.char = char
		# Find words in this region
		visible_region = self.view.visible_region()
		next_search = visible_region.begin()
		last_search = visible_region.end()
		# label A is nr 1, not 0
		index = 1
		SublimeJump_WORDS = []
		#self.edit = self.view.begin_edit("SublimeJumpHints")

		while next_search < last_search:
			# find_all searches in entire file and we don't want this
			# Escape special characters, you can search them too!
			word = self.view.find(selection_regex % escape(self.char), next_search)

			if word:
				SublimeJump_WORDS.append(word)
				label = number_to_letters(index)
				label_length = len(label)
				hint_region = sublime.Region( word.begin(), word.begin() + label_length)

				# Don't replace line ending with label
				if label_length > 1 and match(r'$', self.view.substr(word.begin() + label_length - 1)):
					replace_region = sublime.Region(word.begin(), word.begin() + 1)
					#print("not replacing line ending", label)
				else:
					replace_region = hint_region

				self.view.replace(edit, replace_region, label)
				hints.append(replace_region)
				index += 1
				# print(index, label)
			else:
				#print("no words left", next_search, last_search)
				break

			next_search = word.end()

		# print("no search area left", next_search, last_search)
		matches = len(SublimeJump_WORDS)

		if not matches:
			self.view.set_status("SublimeJump", "No matches found")

		SublimeJump_HAS_LABELS = True
		# Which scope use here, string?
		# comment, string

		if(highlight_match):
			self.view.add_regions("SublimeJumpWords", SublimeJump_WORDS, "comment")

		self.view.add_regions("SublimeJumpHints", hints, "string")
		self.view.set_status(
			"SublimeJump", "Found %d match%s for character %s"
			% (matches, "es" if matches > 1 else "", self.char)
		)


class JumpToRegionCommand(sublime_plugin.TextCommand):

	def run(self, edit, start, end):
		# print('SELECT REGION COMMAND')
		# Checking? try/except
		region = sublime.Region(int(start), int(end))

		if not region:
			# print("JumpToRegion: Bad region!")
			return

		self.view.sel().clear()
		self.view.sel().add(region)
		self.view.show(region)


class JumpToRegionsCommand(sublime_plugin.TextCommand):

	def run(self, edit, start, end):
		# Checking? try/except
		# print('SELECT REGIONSSSS COMMAND')
		region = sublime.Region(int(start), int(end))

		if not region:
			# print("JumpToRegion: Bad region!")
			return

		self.view.sel().clear()
		word_to_find = self.view.substr(region)
		words = self.view.find_all(word_to_find)
		for word in words:
			self.view.sel().add(word)
		self.view.show(region)


class JumpToPlaceCommand(sublime_plugin.TextCommand):

	def run(self, edit, start):
		# Should I do checking for correct number?
		self.view.sel().clear()
		self.view.sel().add(sublime.Region(int(start)))
		self.view.show(int(start))
