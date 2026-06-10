//=============================================================================
// CompletionTracker.js
// HUD and auto-tracking for explore completion (People Met / %).
//=============================================================================
/*:
 * @target MZ
 * @plugindesc v1.0 On-map % complete tracker using game variables 1 and 2.
 * @author Obliviosa
 *
 * @help CompletionTracker.js
 *
 * Uses Variable 1 ("People Met") as the interaction count and Variable 2 ("%")
 * as the completion percentage. NPCs already increment Variable 1 via events;
 * tagged interactables are counted on first interaction.
 *
 * @param countVariableId
 * @text Count Variable
 * @type variable
 * @default 1
 * @desc Variable that stores how many NPCs/interactables have been found.
 *
 * @param percentVariableId
 * @text Percent Variable
 * @type variable
 * @default 2
 * @desc Variable that stores completion percentage (0-100).
 *
 * @param interactNoteTag
 * @text Interactable Note Tag
 * @default auto-added interactable
 * @desc Must match SubtleInteractHint / prop events.
 *
 * @param label
 * @text HUD Label
 * @default Explore
 *
 * @param showOnMap
 * @text Show On Map
 * @type boolean
 * @default true
 *
 * @param hudX
 * @text HUD X
 * @type number
 * @min 0
 * @default 580
 *
 * @param hudY
 * @text HUD Y
 * @type number
 * @min 0
 * @default 8
 *
 * @param hudWidth
 * @text HUD Width
 * @type number
 * @min 80
 * @default 220
 *
 * @license MIT
 */
(() => {
    "use strict";

    const pluginName = "CompletionTracker";
    const params = PluginManager.parameters(pluginName);
    const COUNT_VAR = Number(params.countVariableId || 1);
    const PERCENT_VAR = Number(params.percentVariableId || 2);
    const INTERACT_TAG = String(params.interactNoteTag || "auto-added interactable");
    const HUD_LABEL = String(params.label || "Explore");
    const SHOW_ON_MAP = params.showOnMap !== "false";
    const HUD_X = Number(params.hudX || 580);
    const HUD_Y = Number(params.hudY || 8);
    const HUD_WIDTH = Number(params.hudWidth || 220);

    const NPC_COUNTER_PATTERN = /"code":111,"indent":0,"parameters":\[2,"A",1\].*?"code":122,"indent":1,"parameters":\[1,1,1,0,1\]/;

    //-----------------------------------------------------------------------------
    // CompletionTracker
    //-----------------------------------------------------------------------------

    const CompletionTracker = {
        _totalTargets: 0,

        init() {
            this._totalTargets = this.scanTotalTargets();
        },

        scanTotalTargets() {
            let total = 0;
            if (!$dataMapInfos) {
                return 0;
            }
            for (let mapId = 1; mapId < $dataMapInfos.length; mapId++) {
                if (!$dataMapInfos[mapId]) {
                    continue;
                }
                const map = this.loadMapData(mapId);
                if (!map || !map.events) {
                    continue;
                }
                for (const event of map.events) {
                    if (event && this.isCountableEvent(event)) {
                        total++;
                    }
                }
            }
            return total;
        },

        loadMapData(mapId) {
            const filename = "data/Map%1.json".format(mapId.padZero(3));
            try {
                const xhr = new XMLHttpRequest();
                xhr.open("GET", filename, false);
                xhr.overrideMimeType("application/json");
                xhr.send();
                if (xhr.status < 400) {
                    return JSON.parse(xhr.responseText);
                }
            } catch (e) {
                // Missing or unreadable map file (e.g. deleted map slot).
            }
            return null;
        },

        isInteractableNote(note) {
            return !!(note && note.includes(INTERACT_TAG));
        },

        eventHasNpcCounter(event) {
            const pages = event.pages || [];
            for (const page of pages) {
                const list = page.list || [];
                if (list.length < 2) {
                    continue;
                }
                const serialized = JSON.stringify(list);
                if (NPC_COUNTER_PATTERN.test(serialized)) {
                    return true;
                }
            }
            return false;
        },

        isCountableEvent(event) {
            if (this.isInteractableNote(event.note)) {
                return true;
            }
            return this.eventHasNpcCounter(event);
        },

        isInteractableOnly(event) {
            return (
                this.isInteractableNote(event.note) &&
                !this.eventHasNpcCounter(event)
            );
        },

        selfSwitchKey(mapId, eventId, letter = "A") {
            return [mapId, eventId, letter];
        },

        isSelfSwitchOff(mapId, eventId, letter = "A") {
            if (!$gameSelfSwitches) {
                return true;
            }
            return !$gameSelfSwitches.value(this.selfSwitchKey(mapId, eventId, letter));
        },

        setSelfSwitchOn(mapId, eventId, letter = "A") {
            if (!$gameSelfSwitches) {
                return;
            }
            $gameSelfSwitches.setValue(this.selfSwitchKey(mapId, eventId, letter), true);
        },

        onEventStarted(event) {
            if (!$gameMap || !event || event._erased) {
                return;
            }
            const eventData = event.event();
            if (!eventData || !event.isTriggerIn([0])) {
                return;
            }
            const list = event.list();
            if (!list || list.length <= 1) {
                return;
            }
            if (!this.isInteractableOnly(eventData)) {
                return;
            }
            const mapId = $gameMap.mapId();
            const eventId = event.eventId();
            if (!this.isSelfSwitchOff(mapId, eventId)) {
                return;
            }
            this.setSelfSwitchOn(mapId, eventId);
            if (!$gameVariables) {
                return;
            }
            const count = $gameVariables.value(COUNT_VAR);
            $gameVariables.setValue(COUNT_VAR, count + 1);
        },

        refreshPercent() {
            if (!$gameVariables) {
                return 0;
            }
            const total = Math.max(1, this._totalTargets || this.scanTotalTargets());
            const count = Math.max(0, $gameVariables.value(COUNT_VAR));
            const clamped = Math.min(count, total);
            const percent = Math.floor((clamped * 100) / total);
            if ($gameVariables.value(PERCENT_VAR) !== percent) {
                $gameVariables.setValue(PERCENT_VAR, percent);
            }
            return percent;
        },

        percent() {
            return this.refreshPercent();
        },

        hudText() {
            return `${HUD_LABEL}: ${this.percent()}%`;
        }
    };

    //-----------------------------------------------------------------------------
    // Window_CompletionTracker
    //-----------------------------------------------------------------------------

    function Window_CompletionTracker() {
        this.initialize(...arguments);
    }

    Window_CompletionTracker.prototype = Object.create(Window_Base.prototype);
    Window_CompletionTracker.prototype.constructor = Window_CompletionTracker;

    Window_CompletionTracker.prototype.initialize = function(rect) {
        Window_Base.prototype.initialize.call(this, rect);
        this.opacity = 0;
        this._lastPercent = -1;
        this.refresh();
    };

    Window_CompletionTracker.prototype.update = function() {
        Window_Base.prototype.update.call(this);
        const percent = CompletionTracker.percent();
        if (percent !== this._lastPercent) {
            this.refresh();
        }
    };

    Window_CompletionTracker.prototype.refresh = function() {
        this._lastPercent = CompletionTracker.percent();
        this.contents.clear();
        this.drawCompletionLabel();
    };

    Window_CompletionTracker.prototype.drawCompletionLabel = function() {
        const text = CompletionTracker.hudText();
        const pad = 8;
        const width = this.innerWidth - pad * 2;
        const height = this.lineHeight();
        this.contents.fontSize = 20;
        this.changeTextColor(ColorManager.systemColor());
        this.drawText(text, pad, 0, width, height, "right");
        this.resetFontSettings();
    };

    //-----------------------------------------------------------------------------
    // Hooks
    //-----------------------------------------------------------------------------

    const _DataManager_isDatabaseLoaded = DataManager.isDatabaseLoaded;
    DataManager.isDatabaseLoaded = function() {
        if (!_DataManager_isDatabaseLoaded.call(this)) {
            return false;
        }
        if (!CompletionTracker._databaseReady) {
            CompletionTracker.init();
            CompletionTracker._databaseReady = true;
        }
        return true;
    };

    const _DataManager_setupNewGame = DataManager.setupNewGame;
    DataManager.setupNewGame = function() {
        _DataManager_setupNewGame.call(this);
        CompletionTracker.refreshPercent();
    };

    const _DataManager_extractSaveContents = DataManager.extractSaveContents;
    DataManager.extractSaveContents = function(contents) {
        _DataManager_extractSaveContents.call(this, contents);
        CompletionTracker.refreshPercent();
    };

    const _Game_Variables_setValue = Game_Variables.prototype.setValue;
    Game_Variables.prototype.setValue = function(variableId, value) {
        _Game_Variables_setValue.call(this, variableId, value);
        if (variableId === COUNT_VAR) {
            CompletionTracker.refreshPercent();
        }
    };

    const _Game_Event_start = Game_Event.prototype.start;
    Game_Event.prototype.start = function() {
        CompletionTracker.onEventStarted(this);
        _Game_Event_start.call(this);
    };

    const _Scene_Map_createAllWindows = Scene_Map.prototype.createAllWindows;
    Scene_Map.prototype.createAllWindows = function() {
        _Scene_Map_createAllWindows.call(this);
        if (SHOW_ON_MAP) {
            this.createCompletionTrackerWindow();
        }
    };

    Scene_Map.prototype.createCompletionTrackerWindow = function() {
        const rect = this.completionTrackerWindowRect();
        this._completionTrackerWindow = new Window_CompletionTracker(rect);
        this.addWindow(this._completionTrackerWindow);
    };

    Scene_Map.prototype.completionTrackerWindowRect = function() {
        const ww = HUD_WIDTH;
        const wh = this.calcWindowHeight(1, false);
        return new Rectangle(HUD_X, HUD_Y, ww, wh);
    };
})();
