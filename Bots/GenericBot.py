import pickle
import asyncio
from threading import Thread
from time import time

from ClientFunctions import checkStartingZone #, teleportStart
		
class GenericBot(Thread):
	def __init__(self, client, id):
		Thread.__init__(self)
		self.client = client
		self.id = id
		self.running, self.paused = True, False
		self.defaultData = {"count" : 0, "time" : time()}
		self.debug = True
		
		def quit(self):
			self.running = False
		
		self.commands = {"q" : (quit, (self,), {})}
		
	def run(self):
		asyncio.run(self.run_())
	
	async def run_(self):
		await self.onStart()
		while self.running:
			while self.paused:
				await self.onPause()
			op, t, timeoutFunction = next(self.operations) 
			if self.debug: print(f"[{self.client.title}] running: {op.__name__}")
			if t:
				try:
					await asyncio.wait_for(op(self.client), timeout=t)
				except asyncio.TimeoutError:
					print(op.__name__, "timed out")
					await timeoutFunction(self.client)
			else:
				await op(self.client)
			self.saveData()
	
	async def onStart(self):
		self.loadData()
		await self.client.activate_hooks()
		await self.client.mouse_handler.activate_mouseless()
		self.client.title = self.name + str(self.id)
		
		await checkStartingZone(self.client)
		#if self.startingPosition != None:
		#	await teleportStart(self)
		
	# Overwritten by child (usage next(operation) -> (function, timeout seconds, timeout function)
	async def operation(self):
		pass
		
	# Overwritten by child
	async def onPause(self):
		pass
		
	def loadData(self):
		try:
			self.data = pickle.load(open(f"data/{self.name}.p", "rb"))
		except (OSError, IOError) as e:
			self.data = self.defaultData
			pickle.dump(self.data, open(f"data/{self.name}.p", "wb"))
	
	def saveData(self):
		pickle.dump(self.data, open(f"data/{self.name}.p", "wb"))
		
		
	def addData(self, name, defaultValue=0):
		self.data[name] = defaultValue
	
