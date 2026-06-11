//=============================================================================
// CompletionTracker.js
// HUD and auto-tracking for explore completion (People Met / %).
//=============================================================================
/*:
 * @target MZ
 * @plugindesc v1.1 On-map % complete tracker using game variables 1 and 2.
 * @author Obliviosa
 *
 * @help CompletionTracker.js
 *
 * Variable 1 ("People Met") is incremented only by NPC event commands.
 * Completion % counts NPCs (var 1) plus tagged interactables (tracked via
 * self switch A on first examine; this plugin never writes Variable 1).
 *
 * Target totals are read from data/CompletionTargets.json. Regenerate after
 * adding NPCs or interactables: python3 tools/generate_completion_targets.py
 *
 * @param countVariableId
 * @text People Met Variable
 * @type variable
 * @default 1
 * @desc NPC dialogue counter (incremented by events, not this plugin).
 *
 * @param interactNoteTag
 * @text Interactable Note Tag
 * @default auto-added interactable
 * @desc Must match SubtleInteractHint / prop events.
 *
 * @param percentVariableId
 * @text Percent Variable
 * @type variable
 * @default 2
 * @desc Variable that stores completion percentage (0-100).
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
    const TARGETS_FILE = "data/CompletionTargets.json";

    //-----------------------------------------------------------------------------
    // CompletionTracker
    //-----------------------------------------------------------------------------

    const CompletionTracker = {
        _totalTargets: 0,
        _interactableTargets: [],
        _interactablesFound: -1,
        _cachedPercent: -1,

        init() {
            this._totalTargets = 0;
            this._interactableTargets = [];
            this._interactablesFound = -1;
            this._cachedPercent = -1;
            if (!this.loadTargetsManifest()) {
                this.scanTargetsAsync();
            }
        },

        loadTargetsManifest() {
            try {
                const xhr = new XMLHttpRequest();
                xhr.open("GET", TARGETS_FILE, false);
                xhr.overrideMimeType("application/json");
                xhr.send();
                if (xhr.status < 400) {
                    this.applyTargets(JSON.parse(xhr.responseText));
                    return true;
                }
            } catch (e) {
                // Missing or unreadable manifest.
            }
            return false;
        },

        applyTargets(data) {
            if (!data) {
                return;
            }
            this._totalTargets = Number(data.totalTargets) || 0;
            this._interactableTargets = Array.isArray(data.interactableTargets)
                ? data.interactableTargets
                : [];
            this.invalidateProgressCache();
            this.refreshPercent();
        },

        scanTargetsAsync() {
            if (this._scanActive || !$dataMapInfos) {
                return;
            }
            this._scanActive = true;
            let total = 0;
            const interactables = [];
            const mapIds = [];
            for (let mapId = 1; mapId < $dataMapInfos.length; mapId++) {
                if ($dataMapInfos[mapId]) {
                    mapIds.push(mapId);
                }
            }
            const processMap = index => {
                if (index >= mapIds.length) {
                    this._totalTargets = total;
                    this._interactableTargets = interactables;
                    this._scanActive = false;
                    this.invalidateProgressCache();
                    this.refreshPercent();
                    return;
                }
                const mapId = mapIds[index];
                const filename = "data/Map%1.json".format(mapId.padZero(3));
                const xhr = new XMLHttpRequest();
                xhr.open("GET", filename);
                xhr.overrideMimeType("application/json");
                xhr.onload = () => {
                    if (xhr.status < 400) {
                        try {
                            const map = JSON.parse(xhr.responseText);
                            if (map && map.events) {
                                for (const event of map.events) {
                                    if (!event) {
                                        continue;
                                    }
                                    const hasInteractTag = this.isInteractableNote(event.note);
                                    const hasNpcCounter = this.eventHasNpcCounter(event);
                                    if (!hasInteractTag && !hasNpcCounter) {
                                        continue;
                                    }
                                    total++;
                                    if (hasInteractTag && !hasNpcCounter) {
                                        interactables.push({ mapId, eventId: event.id });
                                    }
                                }
                            }
                        } catch (e) {
                            // Skip unreadable map data.
                        }
                    }
                    processMap(index + 1);
                };
                xhr.onerror = () => processMap(index + 1);
                xhr.send();
            };
            processMap(0);
        },

        isInteractableNote(note) {
            return !!(note && note.includes(INTERACT_TAG));
        },

        eventHasNpcCounter(event) {
            const pages = event.pages || [];
            for (const page of pages) {
                const list = page.list || [];
                for (let i = 0; i < list.length - 1; i++) {
                    const cmd = list[i];
                    const next = list[i + 1];
                    if (
                        cmd.code === 111 &&
                        cmd.indent === 0 &&
                        cmd.parameters[0] === 2 &&
                        cmd.parameters[1] === "A" &&
                        cmd.parameters[2] === 1 &&
                        next.code === 122 &&
                        next.indent === 1 &&
                        next.parameters[0] === COUNT_VAR &&
                        next.parameters[1] === COUNT_VAR &&
                        next.parameters[2] === 1 &&
                        next.parameters[3] === 0 &&
                        next.parameters[4] === 1
                    ) {
                        return true;
                    }
                }
            }
            return false;
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

        isSelfSwitchOn(mapId, eventId, letter = "A") {
            if (!$gameSelfSwitches) {
                return false;
            }
            return !!$gameSelfSwitches.value(this.selfSwitchKey(mapId, eventId, letter));
        },

        setSelfSwitchOn(mapId, eventId, letter = "A") {
            if (!$gameSelfSwitches) {
                return;
            }
            $gameSelfSwitches.setValue(this.selfSwitchKey(mapId, eventId, letter), true);
            this.invalidateProgressCache();
        },

        invalidateProgressCache() {
            this._interactablesFound = -1;
            this._cachedPercent = -1;
        },

        countInteractablesFound() {
            if (this._interactablesFound >= 0) {
                return this._interactablesFound;
            }
            if (!$gameSelfSwitches || !this._interactableTargets.length) {
                this._interactablesFound = 0;
                return 0;
            }
            let found = 0;
            for (const target of this._interactableTargets) {
                if (this.isSelfSwitchOn(target.mapId, target.eventId)) {
                    found++;
                }
            }
            this._interactablesFound = found;
            return found;
        },

        progressCount() {
            const peopleMet = $gameVariables ? Math.max(0, $gameVariables.value(COUNT_VAR)) : 0;
            return peopleMet + this.countInteractablesFound();
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
            if (this.isSelfSwitchOn(mapId, eventId)) {
                return;
            }
            this.setSelfSwitchOn(mapId, eventId);
            this.refreshPercent();
        },

        refreshPercent() {
            if (!$gameVariables) {
                return 0;
            }
            const total = Math.max(1, this._totalTargets || 0);
            const count = this.progressCount();
            const clamped = Math.min(count, total);
            const percent = Math.floor((clamped * 100) / total);
            this._cachedPercent = percent;
            if ($gameVariables.value(PERCENT_VAR) !== percent) {
                $gameVariables.setValue(PERCENT_VAR, percent);
            }
            return percent;
        },

        percent() {
            if (this._cachedPercent >= 0) {
                return this._cachedPercent;
            }
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
            this.refresh(percent);
        }
    };

    Window_CompletionTracker.prototype.refresh = function(percent) {
        const value = percent ?? CompletionTracker.percent();
        this._lastPercent = value;
        this.contents.clear();
        this.drawCompletionLabel(value);
    };

    Window_CompletionTracker.prototype.drawCompletionLabel = function(percent) {
        const text = `${HUD_LABEL}: ${percent}%`;
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
        CompletionTracker.invalidateProgressCache();
        CompletionTracker.refreshPercent();
    };

    const _DataManager_extractSaveContents = DataManager.extractSaveContents;
    DataManager.extractSaveContents = function(contents) {
        _DataManager_extractSaveContents.call(this, contents);
        CompletionTracker.invalidateProgressCache();
        CompletionTracker.refreshPercent();
    };

    const _Game_Variables_setValue = Game_Variables.prototype.setValue;
    Game_Variables.prototype.setValue = function(variableId, value) {
        _Game_Variables_setValue.call(this, variableId, value);
        if (variableId === COUNT_VAR) {
            CompletionTracker.invalidateProgressCache();
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
