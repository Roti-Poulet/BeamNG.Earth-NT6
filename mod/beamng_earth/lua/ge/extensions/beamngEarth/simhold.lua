-- The mod's holds (the drop hold, core.lua; the edge guard, edgeguard.lua): the ground under the player is not there
-- yet, so nothing may move until it is. In single player the game's own pause (simTimeAuthority, what the pause key
-- does). In a BeamMP session that pause stopped every car on this player's screen, the other players' too, for the
-- seconds the ground took (BeamMP blocks the menu's pause requests but not this call): the 1.6.0 players' "multiplayer
-- freezing" (2026-10-23; a two-player test: a drop 2.5 km off the block held 3.4 s). There only our own car is held,
-- its physics off (setActive 0, as vehicle pooling does), and the others drive on.
local M = {}

local heldId = nil          -- the vehicle id held (BeamMP), nil when none

function M.mpSession()
  local n = rawget(_G, 'MPCoreNetwork')
  return n ~= nil and n.isMPSession ~= nil and n.isMPSession() == true
end

local function sta() return rawget(_G, 'simTimeAuthority') end

-- Is the player held (ours, or the game paused)?
function M.paused()
  if heldId then return true end
  local s = sta()
  return s and s.getPause and s.getPause() or false
end

-- Hold (on) or let go: the game's pause, or in a BeamMP session the player's own car only.
function M.pause(on)
  if on then
    if M.mpSession() then
      local veh = rawget(_G, 'getPlayerVehicle') and getPlayerVehicle(0)
      if veh and veh.setActive then
        veh:setActive(0)
        heldId = veh:getID()
        local s = sta()
        log('I', 'beamngEarth', 'BeamMP: our car held (the game runs on: paused ' ..
          tostring(s and s.getPause and s.getPause() or false) .. ')')
        return
      end
    end
    local s = sta()
    if s and s.pause then s.pause(true) end
    return
  end
  if heldId then
    local get = rawget(_G, 'getObjectByID')
    local veh = get and get(heldId)
    if veh and veh.setActive then veh:setActive(1) end
    heldId = nil
    log('I', 'beamngEarth', 'BeamMP: our car let go')
    return
  end
  local s = sta()
  if s and s.pause then s.pause(false) end
end

-- Our own car held (BeamMP), rather than the game paused?
function M.carHeld() return heldId ~= nil end

return M
