# client functions
'''
	functions will need wrappers to time themselves out, check for zones, etc


'''

import asyncio
import os
from time import time
from typing import *
from functools import partial

from wizwalker.constants import Keycode
from wizwalker.extensions.wizsprinter import SprintyCombat, CombatConfigProvider, WizSprinter
from wizwalker.client import Client
from wizwalker.memory import DynamicClientObject
from wizwalker.errors import MemoryReadError
from wizwalker import utils

#TEST
async def goToNearestMob(client):
	await goToClosestOf(client, await client.get_mobs(None))
	
#TEST
async def goToClosestOf(client, entities):
	if entity := await client.find_closest_of_entities(entities, True):
		location = await e.location()
		await client.goto(location.x, location.y)
	
#TEST
async def eatHealth(client):
	await goToClosestOf(client, await client.get_health_wisps(None), False)

#TEST
async def eatMana(client):
	await goToClosestOf(client, await client.get_mana_wisps(None), False)

#TEST
async def goHome(client, cd = 27):
	if hasattr(client, 'teleportCooldown') and time() - client.teleportCooldown < cd:
		await asyncio.sleep(cd - time() + client.teleportCooldown)
	await client.send_key(Keycode.HOME, 0.1)
	await client.wait_for_zone_change()
	client.teleportCooldown = time()

#TEST
async def openWorldGate(client):
	await goHome(client)
	while not await client.is_in_npc_range():
		await client.send_key(Keycode.S, 0.1)
	await client.send_key(Keycode.X, 0.1)
	await asyncio.sleep(.2)
	
#TEST
async def goToWizardCity(client):
	await openWorldGate(client)
	for _ in range(5):
		await client.mouse_handler.click_window_with_name('leftButton')
	await client.mouse_handler.click_window_with_name('wbtnWizardCity')
	await asyncio.sleep(0.1)
	await client.mouse_handler.click_window_with_name('teleportButton')
	#await asyncio.sleep(0.1) Might be redundent
	await client.wait_for_zone_change()
	
#TEST
async def spiralTreeToCommons(client):
	await client.teleport(XYZ(-7.503681, -3141.505859, 244.030518), False)
	await client.send_key(Keycode.A, 0.1)
	#await asyncio.sleep(0.1) Might be redundent
	await client.wait_for_zone_change()
	await client.teleport(XYZ(-1.195801, -2155.578125, -153.288666), False)
	await client.send_key(Keycode.A, 0.1)
	#await asyncio.sleep(0.1) Might be redundent
	await client.wait_for_zone_change()

#TEST
async def mark(client):
	await client.send_key(Keycode.A, 0.1)
	await asyncio.sleep(0.8)
	await client.send_key(Keycode.PAGE_DOWN, 0.1)
	await asyncio.sleep(0.1)
	
#TEST
async def unmark(client):
	await client.send_key(Keycode.PAGE_UP, 0.1)
	await client.wait_for_zone_change()

#TEST
async def healIfNeeded(client):
	await client.use_potion_if_needed(health_percent=65, mana_percent=5)
	if await client.needs_potion(health_percent=65, mana_percent=5) and not await client.has_potion():
		if await client.stats.current_gold() >= 25000: 
			await mark(client)
			await buyPotions(client)
			await unmark(client)
			await mark(client)
			
#TEST
async def eatWisps(client):
	health = await client.stats.max_hitpoints()
	if await client.stats.current_hitpoints() < 0.3 * health:
			await eatHealth(client)

	mana = await client.stats.max_mana()
	if await client.stats.current_mana() < 0.3 * mana:
			await eatMana(client)
			
	await asyncio.sleep(0.1)

#TEST
async def buyPotions(client):
	await goToWizardCity(client)
	await spiralTreeToCommons(client)
	
	# Might be redundent
	#await client.teleport(XYZ(-4352.091797, 1111.261230, 229.000793), False)
	#await client.send_key(Keycode.A, 0.1)
	#await asyncio.sleep(0.5)
	
	# TP to potion vendor
	while not await client.is_in_npc_range():
		await client.teleport(XYZ(-4352.091797, 1111.261230, 229.000793), False)
		await client.send_key(Keycode.A, 0.1)
		await asyncio.sleep(.5)
	await client.send_key(Keycode.X, 0.1)
	await asyncio.sleep(.1) # testing .1, was set to 1
	
	# Buy potions
	await client.mouse_handler.click_window_with_name("fillallpotions")
	await asyncio.sleep(.1) # testing .1, was set to 1
	await client.mouse_handler.click_window_with_name("buyAction")
	await asyncio.sleep(.1)
	await client.mouse_handler.click_window_with_name("btnShopPotions")
	await asyncio.sleep(.1)
	await client.mouse_handler.click_window_with_name("centerButton")
	await asyncio.sleep(.1)
	await client.mouse_handler.click_window_with_name("fillonepotion")
	await asyncio.sleep(.1)
	await client.mouse_handler.click_window_with_name("buyAction")
	await asyncio.sleep(.1)
	await client.mouse_handler.click_window_with_name("exit")
	await asyncio.sleep(.1)

#TEST
async def teamup(client):
	await client.mouse_handler.click_window_with_name('TeamUpButton')
	await asyncio.sleep(0.7)
	await client.mouse_handler.click_window_with_name('TeamSize4CheckBox')
	await asyncio.sleep(0.1)
	await client.mouse_handler.click_window_with_name('TeamTypeFarmingCheckBox')
	await asyncio.sleep(0.1)
	await clickWindowFromPath(client, ["WorldView", "TeamUpConfirmationWindow", "TeamUpConfirmationBackground", "TeamUpButton"])
	
#TEST
async def getWindowFromPath(root_window, name_path):
	async def _recurse_follow_path(window, path):
		if len(path) == 0:
			return window

		for child in await window.children():
			if await child.name() == path[0]:
				found_window = await _recurse_follow_path(child, path[1:])
				if not found_window is False:
					return found_window

		return False

	return await _recurse_follow_path(root_window, name_path)

#TEST, will also test getWindowFromPath
async def clickWindowFromPath(client, path_array):
	coro = partial(getWindowFromPath, client.root_window, path_array)
	window = await utils.wait_for_non_error(coro)
	await client.mouse_handler.click_window(window)

#TEST
async def quickSellAll(client, crownItems = False):
	# need to be on first sell page (all items) to function correctly (should add a click for this)
	await client.send_key(Keycode.B, 0.3)
	await asyncio.sleep(0.1)
	await client.mouse_handler.click_window_with_name('QuickSell_Item')
	await asyncio.sleep(0.1)
	await client.mouse_handler.click_window_with_name('AllAction')
	await asyncio.sleep(0.1)
	
	# line below needs a timeout
	await client.mouse_handler.click_window_with_name("rightButton" if not crownItems else "centerButton")
	await asyncio.sleep(0.1)
	await client.mouse_handler.click_window_with_name('sellAction')
	await asyncio.sleep(0.1)
	await client.mouse_handler.click_window_with_name('SellButton')
	await asyncio.sleep(0.1)
	await client.send_key(Keycode.B, .3)
	await asyncio.sleep(0.5)

#TEST, should be generalized or broken up into components
async def reset(client):
	await client.teleport(XYZ(12.702668190002441,1612.439208984375, 0), False)
	await asyncio.sleep(0.1)
	await client.send_key(Keycode.A, 0.1)
	await asyncio.sleep(0.1)
	await client.wait_for_zone_change()
	await asyncio.sleep(0.1)
	await client.goto(-3136.481689453125, 464.997802734375)
	await asyncio.sleep(0.7)

#TEST
async def unghost(client, repeat=5):
	await asyncio.sleep(0.4)
	for _ in range(repeat):
		await client.send_key(Keycode.S, .3)
		await client.send_key(Keycode.W, .3)

#TEST used for battle
class CombatWrapper(SprintyCombat):
	async def get_client_member(self):
		return await utils.wait_for_non_error(super().get_client_member)

#TEST
async def battle(client):
	try:
		config = CombatConfigProvider(f'configs/{client.title}spellconfig.txt', cast_time=.5,)
	except FileNotFoundError:
		newConfig = open(f'configs/{client.title}spellconfig.txt', "a")
		newConfig.close()
		config = CombatConfigProvider(f'configs/{client.title}spellconfig.txt', cast_time=.5,)
	
	combat = SprintyCombat(client, config)
	try:
		await combat.wait_for_combat()
	except: 
		await battle(client)
	await asyncio.sleep(0.1)

#TEST
async def checkStartingZone(client):
	if client.startingZone:
		zone = await client.zone_name()
		assert zone == client.startingZone
	

async def defaultTimeout(*args, **kwargs):
	return
