//=============================================================================
// HideMenuGold.js
// Removes the unused gold window from the main menu only.
//=============================================================================
/*:
 * @target MZ
 * @plugindesc v1.1 Hides the main menu gold window (unused in this game).
 * @author Obliviosa
 *
 * @help HideMenuGold.js
 *
 * Load this plugin BELOW VisuStella Core Engine and Main Menu Core.
 *
 * Hides the gold window and fixes bottom-bar layout for playtime + variables
 * when using Command Window Style: mobile (or top/thinTop).
 *
 * @param playtimeWidth
 * @text Playtime Column Width
 * @type number
 * @min 120
 * @default 220
 * @desc Width reserved for the playtime block on the left of the bottom bar.
 *
 * @license MIT
 */
(() => {
    "use strict";

    const pluginName = "HideMenuGold";
    const params = PluginManager.parameters(pluginName);
    const PLAYTIME_WIDTH = Number(params.playtimeWidth || 220);

    const refreshBottomWindows = function(scene) {
        const playtime = scene._playtimeWindow;
        if (playtime && scene.canCreatePlaytimeWindow?.()) {
            const playRect = scene.playtimeWindowRect();
            playtime.move(playRect.x, playRect.y, playRect.width, playRect.height);
            playtime.refresh();
        }
        const variable = scene._variableWindow;
        if (variable && scene.canCreateVariableWindow?.()) {
            const varRect = scene.variableWindowRect();
            variable.move(varRect.x, varRect.y, varRect.width, varRect.height);
            variable.refresh();
        }
    };

    // Mobile / top styles: playtime on the left, variables fill the rest of the bar.
    Scene_Menu.prototype.playtimeWindowRectTopStyle = function() {
        const wh = this.calcWindowHeight(1, false);
        const wy = this.mainAreaBottom() - wh;
        return new Rectangle(0, wy, PLAYTIME_WIDTH, wh);
    };

    Scene_Menu.prototype.variableWindowRectTopStyle = function() {
        const wh = this.calcWindowHeight(1, false);
        const wy = this.mainAreaBottom() - wh;
        const playtimeWidth = this._playtimeWindow
            ? this._playtimeWindow.width
            : PLAYTIME_WIDTH;
        const wx = playtimeWidth;
        const ww = Graphics.boxWidth - wx;
        return new Rectangle(wx, wy, ww, wh);
    };

    // Stub window satisfies VisuMZ layout checks without building a full gold UI.
    Scene_Menu.prototype.createGoldWindow = function() {
        const rect = new Rectangle(0, 0, 0, 0);
        this._goldWindow = new Window_Base(rect);
        this._goldWindow.visible = false;
        this.addWindow(this._goldWindow);
    };

    const _Scene_Menu_create = Scene_Menu.prototype.create;
    Scene_Menu.prototype.create = function() {
        _Scene_Menu_create.call(this);
        refreshBottomWindows(this);
    };
})();
