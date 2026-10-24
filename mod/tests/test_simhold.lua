-- luajit mod/tests/test_simhold.lua  (the mod's holds: the game's pause alone, our own car only in a BeamMP session)
local T = dofile((arg[0]:match('^(.*)[/\\]') or '.') .. '/testlib.lua')
log = log or function() end
local H = require('beamngEarth/simhold')

local pausedSim = false
simTimeAuthority = { pause = function(on) pausedSim = on end, getPause = function() return pausedSim end }
local car = { id = 7, active = 1 }
function car:setActive(a) self.active = a end
function car:getID() return self.id end
getPlayerVehicle = function() return car end
getObjectByID = function(id) return id == car.id and car or nil end

-- single player: the game's pause
H.pause(true)
T.check(pausedSim and H.paused() and not H.carHeld() and car.active == 1, 'single player: the game paused, the car as it is')
H.pause(false)
T.check(not pausedSim and not H.paused(), 'single player: resumed')

-- a BeamMP session: only our car held (the other players' cars keep moving on our screen)
MPCoreNetwork = { isMPSession = function() return true end }
H.pause(true)
T.check(not pausedSim and car.active == 0 and H.paused() and H.carHeld(), 'BeamMP: our car held, the game not paused')
H.pause(false)
T.check(car.active == 1 and not H.paused() and not H.carHeld(), 'BeamMP: our car let go')
MPCoreNetwork = nil
T.done('test_simhold')
