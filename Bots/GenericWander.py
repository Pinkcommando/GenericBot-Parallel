import asyncio
from time import time
from ClientFunctions import *
from Bots.GenericBot import GenericBot

class Wander(GenericBot):
	async def onStart(self):
		self.name = "Wander"
		self.client.startingZone = None
		self.client.startingPosition = None
		self.operations = self.operation()
		await super().onStart()
		#await mark(self.client)
	
	def operation(self):
		while True:
			yield (healIfNeeded, None, defaultTimeout)
			yield (unghost, None, defaultTimeout) 
			yield (goToNearestMob, None, defaultTimeout) 
			yield (battle, None, defaultTimeout) 
			
			self.data["count"] += 1
			print(f"[{self.client.title}] cycle finished run #{self.data['count']}")
			#self.consoleOut()
			
			if self.data["count"] % 20 == 2: 
				yield (quickSellAll, None, defaultTimeout) 