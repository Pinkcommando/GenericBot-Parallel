from threading import Thread
import asyncio
import traceback

from wizwalker.extensions.wizsprinter import WizSprinter
from Bots.GenericBot import GenericBot
from Bots.GenericWander import Wander
		
'''
	Generate clients
	Assign Clients to a bot
'''

'''
	Commands
	
	lc:
		list clients
	
	lb:
		list bots
	
	lt: 
		list bot types
		
	a(client, type):
		assigns client to bot type
		
	s(client):
		starts client
		
	x(client):
		stops client
		
	q:
		quit all
		
	

'''
def quit(self):
	self.running = False
	for bot in self.bots:
		bot.running = False
		
def listClients(self):
	print(self.clients)
		
def listBots(self):
	print(self.bots)
	
def listTypes(self):
	for a, b in self.types:
		print(f"{a}: {b}")
		
def startBot(self, i=0):
	try:
		self.bots[i].start()
	except:
		traceback.print_exc()
		
class BotRunner(WizSprinter):
	def __init__(self):
		super().__init__()
		self.running = True
		self.debug = False
		
		commands = {
			"q" : (quit, (self,), {}),
			"lc" : (listClients, (self,), {}),
			"lb" : (listBots, (self,), {}),
			"lt" : (listTypes, (self,), {}),
			"s" : (startBot, (self,), {})
		}
			
		botTypes = {
			"wander" : Wander
		}
		
		# start console input 
		self.input = UserInput(self)
		self.input.start()
		
		# populate clients
		self.get_new_clients()
		self.bots = [None] * len(self.clients)
		self.bots = [Wander(client, id) for id, client in enumerate(self.clients)] # remove later
		
	
	def startBot(self, i=0):
		try:
			self.bots[i].start()
		except:
			traceback.print_exc()

				
	async def run(self):
		for i in range(len(self.bots)):
			self.startBot(i)
		

class UserInput(Thread):
	def __init__(self, bot : GenericBot):
		Thread.__init__(self)
		self.bot = bot
		
	def run(self):
		while self.bot.running:
			inp, *args_ = input()
			if inp in self.bot.commands:
				func, args, kwargs = self.bot.commands[inp]
				func(*args, *args_, **kwargs)
		self.bot.running = False # in the event of a keyboard interupt

if __name__ == "__main__":
	async def run():
		runner = BotRunner()
		try:
			await runner.run()
		except:
			traceback.print_exc()
		await runner.close()
	asyncio.run(run())