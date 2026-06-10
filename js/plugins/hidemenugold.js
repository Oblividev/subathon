//=============================================================================
// HideMenuGold.js
// Removes the unused gold window from the main menu only.
//=============================================================================
/*:
 * @target MZ
 * @plugindesc v1.0 Hides the main menu gold window (unused in this game).
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

    const hideGoldWindow = function(scene) {
        const gold = scene._goldWindow;
        if (!gold) {
            return;
        }
        gold.visible = false;
        gold.opacity = 0;
        if (gold.close) {
            gold.close();
        }
    };

    const refreshBottomWindows = function(scene) {
        if (scene._playtimeWindow && scene.canCreatePlaytimeWindow?.()) {
            const playRect = scene.playtimeWindowRect();
            scene._playtimeWindow.move(
                playRect.x,
                playRect.y,
                playRect.width,
                playRect.height
            );
            scene._playtimeWindow.refresh();
        }
        if (scene._variableWindow && scene.canCreateVariableWindow?.()) {
            const varRect = scene.variableWindowRect();
            scene._variableWindow.move(
                varRect.x,
                varRect.y,
                varRect.width,
                varRect.height
            );
            scene._variableWindow.refresh();
        }
    };

    // Mobile / top styles: playtime on the left, variables fill the rest of the bar.
    Scene_Menu.prototype.playtimeWindowRectTopStyle = function() {
        const rows = 1;
        const wh = this.calcWindowHeight(rows, false);
        const wy = this.mainAreaBottom() - wh;
        return new Rectangle(0, wy, PLAYTIME_WIDTH, wh);
    };

    Scene_Menu.prototype.variableWindowRectTopStyle = function() {
        const rows = 1;
        const wh = this.calcWindowHeight(rows, false);
        const wy = this.mainAreaBottom() - wh;
        const playtimeWidth = this._playtimeWindow
            ? this._playtimeWindow.width
            : PLAYTIME_WIDTH;
        const wx = playtimeWidth;
        const ww = Graphics.boxWidth - wx;
        return new Rectangle(wx, wy, ww, wh);
    };

    const _Scene_Menu_createGoldWindow = Scene_Menu.prototype.createGoldWindow;
    Scene_Menu.prototype.createGoldWindow = function() {
        _Scene_Menu_createGoldWindow.call(this);
        hideGoldWindow(this);
    };

    const _Scene_Menu_create = Scene_Menu.prototype.create;
    Scene_Menu.prototype.create = function() {
        _Scene_Menu_create.call(this);
        hideGoldWindow(this);
        refreshBottomWindows(this);
    };
})();
