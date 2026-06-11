//=============================================================================
// SubtleInteractHint.js
// Soft proximity cue for events tagged in their note field.
//=============================================================================
/*:
 * @target MZ
 * @plugindesc v1.2 Smaller, softer balloon hint for tagged examine events.
 * @author Obliviosa
 *
 * @help SubtleInteractHint.js
 *
 * Events whose Note contains the tag below get a brief, infrequent balloon
 * only when the player is close enough to press Z. Hints use a scaled-down
 * balloon sprite so they read quieter than story balloons.
 *
 * @param noteTag
 * @text Note Tag
 * @default auto-added interactable
 *
 * @param balloonId
 * @text Balloon Icon
 * @type number
 * @min 1
 * @max 13
 * @default 8
 *
 * @param cooldownFrames
 * @text Cooldown (frames)
 * @type number
 * @min 60
 * @default 300
 *
 * @param requireFacing
 * @text Require Facing / Adjacent
 * @type boolean
 * @default true
 *
 * @param scale
 * @text Hint Scale
 * @type number
 * @decimals 2
 * @min 0.2
 * @max 1
 * @default 0.42
 *
 * @param opacity
 * @text Hint Opacity
 * @type number
 * @decimals 2
 * @min 0.2
 * @max 1
 * @default 0.62
 *
 * @param durationRate
 * @text Duration Multiplier
 * @type number
 * @decimals 2
 * @min 0.2
 * @max 1
 * @default 0.55
 * @desc Lower = shorter on-screen time.
 *
 * @param yOffset
 * @text Vertical Offset (px)
 * @type number
 * @min -24
 * @max 24
 * @default 6
 * @desc Nudge hint closer to the object (positive = lower).
 *
 * @license MIT
 */
(() => {
    "use strict";

    const pluginName = "SubtleInteractHint";
    const params = PluginManager.parameters(pluginName);
    const NOTE_TAG = String(params.noteTag || "auto-added interactable");
    const BALLOON_ID = Number(params.balloonId || 8);
    const COOLDOWN = Number(params.cooldownFrames || 300);
    const REQUIRE_FACING = params.requireFacing !== "false";
    const HINT_SCALE = Number(params.scale || 0.42);
    const HINT_OPACITY = Number(params.opacity || 0.62);
    const DURATION_RATE = Number(params.durationRate || 0.55);
    const Y_OFFSET = Number(params.yOffset || 6);
    const UPDATE_INTERVAL = 8;

    //-----------------------------------------------------------------------------
    // Sprite_SubtleBalloon
    //-----------------------------------------------------------------------------

    function Sprite_SubtleBalloon() {
        this.initialize(...arguments);
    }

    Sprite_SubtleBalloon.prototype = Object.create(Sprite_Balloon.prototype);
    Sprite_SubtleBalloon.prototype.constructor = Sprite_SubtleBalloon;

    Sprite_SubtleBalloon.prototype.setup = function(targetSprite, balloonId) {
        Sprite_Balloon.prototype.setup.call(this, targetSprite, balloonId);
        this._duration = Math.max(8, Math.floor(this._duration * DURATION_RATE));
        this.scale.x = HINT_SCALE;
        this.scale.y = HINT_SCALE;
        this.alpha = HINT_OPACITY;
    };

    Sprite_SubtleBalloon.prototype.waitTime = function() {
        return 4;
    };

    Sprite_SubtleBalloon.prototype.speed = function() {
        return 10;
    };

    Sprite_SubtleBalloon.prototype.updatePosition = function() {
        Sprite_Balloon.prototype.updatePosition.call(this);
        this.y += Y_OFFSET;
    };

    //-----------------------------------------------------------------------------
    // SubtleInteractHint
    //-----------------------------------------------------------------------------

    const SubtleInteractHint = {
        _cooldowns: new Map(),
        _taggedEvents: [],
        _lastPlayerX: -1,
        _lastPlayerY: -1,
        _lastPlayerDir: -1,
        _updateTick: 0,

        clear() {
            this._cooldowns.clear();
            this._taggedEvents = [];
            this._lastPlayerX = -1;
            this._lastPlayerY = -1;
            this._lastPlayerDir = -1;
            this._updateTick = 0;
        },

        key(mapId, eventId) {
            return `${mapId}:${eventId}`;
        },

        onCooldown(mapId, eventId) {
            const until = this._cooldowns.get(this.key(mapId, eventId)) || 0;
            return Graphics.frameCount < until;
        },

        markUsed(mapId, eventId) {
            this._cooldowns.set(
                this.key(mapId, eventId),
                Graphics.frameCount + COOLDOWN
            );
        },

        canShowHints() {
            return (
                $gameMap &&
                $gamePlayer &&
                $gamePlayer.canStartLocalEvents() &&
                !$gameMessage.isBusy() &&
                !$gameMap.isEventRunning() &&
                SceneManager._scene instanceof Scene_Map
            );
        },

        isTaggedEvent(eventData) {
            return !!(eventData && eventData.note && eventData.note.includes(NOTE_TAG));
        },

        rebuildTaggedEvents() {
            this._taggedEvents = [];
            if (!$gameMap) {
                return;
            }
            for (const event of $gameMap.events()) {
                if (event && this.isTaggedEvent(event.event())) {
                    this._taggedEvents.push(event);
                }
            }
        },

        playerContextChanged() {
            const px = $gamePlayer.x;
            const py = $gamePlayer.y;
            const dir = $gamePlayer.direction();
            if (
                px !== this._lastPlayerX ||
                py !== this._lastPlayerY ||
                dir !== this._lastPlayerDir
            ) {
                this._lastPlayerX = px;
                this._lastPlayerY = py;
                this._lastPlayerDir = dir;
                return true;
            }
            return false;
        },

        requestHint(event) {
            const request = {
                target: event,
                balloonId: BALLOON_ID,
                subtle: true
            };
            $gameTemp._balloonQueue.push(request);
            if (event.startBalloon) {
                event.startBalloon();
            }
        },

        playerCanActionButton(event) {
            if (event._erased || event._trigger !== 0) {
                return false;
            }
            const px = $gamePlayer.x;
            const py = $gamePlayer.y;
            const ex = event.x;
            const ey = event.y;

            if (px === ex && py === ey) {
                return true;
            }

            const dir = $gamePlayer.direction();
            const fx = $gameMap.roundXWithDirection(px, dir);
            const fy = $gameMap.roundYWithDirection(py, dir);
            if (fx === ex && fy === ey) {
                return true;
            }

            if ($gameMap.isCounter(fx, fy)) {
                const fx2 = $gameMap.roundXWithDirection(fx, dir);
                const fy2 = $gameMap.roundYWithDirection(fy, dir);
                if (fx2 === ex && fy2 === ey) {
                    return true;
                }
            }

            const dist = Math.abs(px - ex) + Math.abs(py - ey);
            if (dist !== 1) {
                return false;
            }
            const dx = ex - px;
            const dy = ey - py;
            return (
                (dir === 2 && dy === 1) ||
                (dir === 8 && dy === -1) ||
                (dir === 4 && dx === -1) ||
                (dir === 6 && dx === 1)
            );
        },

        nearestHintableEvent() {
            const mapId = $gameMap.mapId();
            let best = null;
            let bestDist = Infinity;
            for (const event of this._taggedEvents) {
                if (event._erased || event.isBalloonPlaying()) {
                    continue;
                }
                if (REQUIRE_FACING && !this.playerCanActionButton(event)) {
                    continue;
                }
                if (this.onCooldown(mapId, event.eventId())) {
                    continue;
                }
                const dist = Math.abs($gamePlayer.x - event.x) + Math.abs($gamePlayer.y - event.y);
                if (dist < bestDist) {
                    bestDist = dist;
                    best = event;
                }
            }
            return best;
        },

        update() {
            if (!this.canShowHints()) {
                return;
            }
            this._updateTick++;
            if (!this.playerContextChanged() && this._updateTick % UPDATE_INTERVAL !== 0) {
                return;
            }
            const event = this.nearestHintableEvent();
            if (!event) {
                return;
            }
            this.requestHint(event);
            this.markUsed($gameMap.mapId(), event.eventId());
        }
    };

    const _Spriteset_Map_createBalloon = Spriteset_Map.prototype.createBalloon;
    Spriteset_Map.prototype.createBalloon = function(request) {
        if (!request.subtle) {
            _Spriteset_Map_createBalloon.call(this, request);
            return;
        }
        const targetSprite = this.findTargetSprite(request.target);
        if (!targetSprite) {
            return;
        }
        const sprite = new Sprite_SubtleBalloon();
        sprite.targetObject = request.target;
        sprite.setup(targetSprite, request.balloonId);
        this._effectsContainer.addChild(sprite);
        this._balloonSprites.push(sprite);
    };

    const _Scene_Map_start = Scene_Map.prototype.start;
    Scene_Map.prototype.start = function() {
        _Scene_Map_start.call(this);
        SubtleInteractHint.clear();
        SubtleInteractHint.rebuildTaggedEvents();
    };

    const _Scene_Map_update = Scene_Map.prototype.update;
    Scene_Map.prototype.update = function() {
        _Scene_Map_update.call(this);
        SubtleInteractHint.update();
    };

    const _Game_Event_clearStartingFlag = Game_Event.prototype.clearStartingFlag;
    Game_Event.prototype.clearStartingFlag = function() {
        _Game_Event_clearStartingFlag.call(this);
        if (SubtleInteractHint.isTaggedEvent(this.event())) {
            SubtleInteractHint.markUsed($gameMap.mapId(), this.eventId());
        }
    };
})();
