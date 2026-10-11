import json
import asyncio

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.scroll_view import ScrollView
from textual.theme import Theme
from textual.widgets import (
	Footer,
	Header,
	Input,
	Label,
	ListItem,
	ListView,
	RichLog,
	Static,
)
from textual_image.widget import Image
from websockets.exceptions import ConnectionClosed

main_theme = Theme(
	name = 'main',
	primary = '#E6E9F0',
	background = '#1B1F2A',
	variables= {
		'border': '#5B3DF5'
	},
	dark = True
)

class ConsoleApp(App):
	BINDINGS = [("ctrl+l", "clear", "Очистить"), ("ctrl+q", "quit", "Выход")]

	CSS = """

		* {
			scrollbar-size: 0 1;
			scrollbar-background: transparent;
		}

		.main {
			border: round $border;
			background: transparent;
		}

		Input {
			border: round;
		}

		.sidebar {
			dock: left;
			width: 15%;
			height: 1fr;
			margin-bottom: 10;
			border: round $border;
			background: transparent;
		}

		.input {
			layout: horizontal;
			height: 3;
			border: round $border;
		}

		.group {
			layout: horizontal;
			min-height: 3;
			align: center middle;
			margin: 0 0 1 0;
		}

		.groupImage {
			height: 3;
			width: 6;
			dock: left;
		}

		.groupLabel {
			width: 1fr;
			text-align: center;
		}

		.input > Input {
			padding: 0;
			width: 0.98fr;
			dock: right;
			border: none;
			background: transparent;
		}

		.input > Static {
			width: 1;
			height: 1;
			margin: 0 0 0 1;
		}

		RichLog {
			background: transparent;
		}
	"""

	def __init__(self, groups: list[dict], inp: asyncio.Queue, out: asyncio.Queue, **kwargs):
		super().__init__(**kwargs)
		self.groups = groups
		self.inp = inp
		self.out = out


	def compose(self) -> ComposeResult:
		yield Container(
			Header(True),
			RichLog(wrap = True, markup = True),
			Container(
				Static(content = '[bold green]>[/]'),
				Input(placeholder = "Вводите..."),
				classes = 'input'
			),
			Footer(),
			classes = "main"
		)

		yield ListView( *[
				ListItem(
					Image(g.get('image', ''), classes = "groupImage"),
					Label(g.get('name', ''), classes = 'groupLabel'),
					id = g.get('id', ''),
					classes="group"
				) for g in self.groups
			],
			classes = "sidebar"
		)

	async def get_messages(self):
		while True:
			self.term.write(await self.out.get())

	async def on_mount(self):
		self.register_theme(main_theme)
		self.theme = "main"
		self.term = self.query_one(RichLog)
		self.query_one(Input).focus()
		self.run_worker(self.get_messages(), exclusive=True)

	async def on_input_submitted(self, event: Input.Submitted) -> None:
		text = event.value.strip()
		event.input.clear()
		if not text:
			return
		self.term.write(f"[bold green]>[/] {text}")
		if text == 'exit':
			self.exit()
		else:
			await self.inp.put(text)

	def action_clear(self):
		self.term.clear()
