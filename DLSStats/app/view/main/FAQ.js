Ext.define("DLSStats.view.main.FAQ", {
    extend: "Ext.container.Container",
    xtype: "dls-faq",

    layout: { type: "vbox", align: "center", pack: "start" },
    padding: 20,
    scrollable: true,

    style: {
        backgroundImage: 'url("./resources/background.jpg")',
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
    },

    items: [
        {
            xtype: "component",
            html: `
            <div style="
                background: rgba(245,245,245,0.97);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 12px;
                padding: 28px 36px;
                max-width: 680px;
                color: #222;
                font-family: Arial, sans-serif;
                font-size: 14px;
                line-height: 1.8;
                box-shadow: 0 4px 24px rgba(0,0,0,0.3);
            ">
                <div style="font-size:20px; font-weight:bold; margin-bottom:20px; border-bottom:2px solid #e0e0e0; padding-bottom:10px; color:#222;">
                    ❓ Frequently Asked Questions
                </div>

                <!-- Q1 -->
                <div style="margin-bottom:18px;">
                    <div style="font-weight:bold; color:#e67e22; margin-bottom:4px;">1. Where do I find a player's ID?</div>
                    <div style="color:#444;">Every player's detail panel shows their ID. Use the <b>Search</b> tab to find a player, then look at the <b>ID</b> field on the right side.</div>
                </div>

                <!-- Q2 -->
                <div style="margin-bottom:18px;">
                    <div style="font-weight:bold; color:#e67e22; margin-bottom:4px;">2. What does each version mean?</div>
                    <table style="border-collapse:collapse; width:100%; margin-top:4px;">
                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:4px 16px 4px 0; color:#2980b9; font-weight:bold; white-space:nowrap;">20231</td>
                            <td style="padding:4px 0; color:#444;">Mid 2023</td>
                        </tr>
                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:4px 16px 4px 0; color:#2980b9; font-weight:bold;">20241</td>
                            <td style="padding:4px 0; color:#444;">December 2023</td>
                        </tr>
                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:4px 16px 4px 0; color:#2980b9; font-weight:bold;">20242</td>
                            <td style="padding:4px 0; color:#444;">May 2024</td>
                        </tr>
                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:4px 16px 4px 0; color:#2980b9; font-weight:bold;">20251</td>
                            <td style="padding:4px 0; color:#444;">December 2024</td>
                        </tr>
                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:4px 16px 4px 0; color:#2980b9; font-weight:bold;">20252</td>
                            <td style="padding:4px 0; color:#444;">February 2025</td>
                        </tr>
                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:4px 16px 4px 0; color:#2980b9; font-weight:bold;">20253</td>
                            <td style="padding:4px 0; color:#444;">June 2025</td>
                        </tr>
                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:4px 16px 4px 0; color:#2980b9; font-weight:bold;">20261</td>
                            <td style="padding:4px 0; color:#444;">December 2025</td>
                        </tr>
                        <tr>
                            <td style="padding:4px 16px 4px 0; color:#e67e22; font-weight:bold;">20262 ★</td>
                            <td style="padding:4px 0; color:#444;">February 2026 <span style="color:#e67e22; font-size:11px; font-weight:bold;">(latest)</span></td>
                        </tr>
                    </table>
                </div>

                <!-- Q3 -->
                <div style="margin-bottom:18px;">
                    <div style="font-weight:bold; color:#e67e22; margin-bottom:4px;">3. What do the stat abbreviations mean?</div>
                    <table style="border-collapse:collapse; width:100%; margin-top:4px;">
                        <tr style="border-bottom:1px solid #eee;"><td style="padding:3px 16px 3px 0; font-weight:bold; color:#2980b9; width:60px;">SPE</td><td style="color:#444;">Speed</td></tr>
                        <tr style="border-bottom:1px solid #eee;"><td style="padding:3px 16px 3px 0; font-weight:bold; color:#2980b9;">ACC</td><td style="color:#444;">Acceleration</td></tr>
                        <tr style="border-bottom:1px solid #eee;"><td style="padding:3px 16px 3px 0; font-weight:bold; color:#2980b9;">STA</td><td style="color:#444;">Stamina &nbsp;<span style="color:#888; font-size:12px;">(GKR = Goalkeeper Reflexes for GK)</span></td></tr>
                        <tr style="border-bottom:1px solid #eee;"><td style="padding:3px 16px 3px 0; font-weight:bold; color:#2980b9;">STR</td><td style="color:#444;">Strength</td></tr>
                        <tr style="border-bottom:1px solid #eee;"><td style="padding:3px 16px 3px 0; font-weight:bold; color:#2980b9;">CON</td><td style="color:#444;">Control</td></tr>
                        <tr style="border-bottom:1px solid #eee;"><td style="padding:3px 16px 3px 0; font-weight:bold; color:#2980b9;">PAS</td><td style="color:#444;">Passing</td></tr>
                        <tr style="border-bottom:1px solid #eee;"><td style="padding:3px 16px 3px 0; font-weight:bold; color:#2980b9;">SHO</td><td style="color:#444;">Shooting &nbsp;<span style="color:#888; font-size:12px;">(GKH = Goalkeeper Handling for GK)</span></td></tr>
                        <tr><td style="padding:3px 16px 3px 0; font-weight:bold; color:#2980b9;">TAC</td><td style="color:#444;">Tackling</td></tr>
                    </table>
                </div>

                <!-- Q4 -->
                <div style="margin-bottom:18px;">
                    <div style="font-weight:bold; color:#e67e22; margin-bottom:4px;">4. What do the stat colors mean?</div>
                    <div style="color:#444; margin-bottom:6px;">In the player detail panel, each stat is color-coded by value:</div>
                    <div style="display:flex; flex-wrap:wrap; gap:8px;">
                        <span style="background:#000; color:cyan; padding:3px 10px; border-radius:4px; font-weight:bold; font-size:13px;">90+ Cyan</span>
                        <span style="background:#000; color:lime; padding:3px 10px; border-radius:4px; font-weight:bold; font-size:13px;">80–89 Lime</span>
                        <span style="background:#000; color:yellow; padding:3px 10px; border-radius:4px; font-weight:bold; font-size:13px;">70–79 Yellow</span>
                        <span style="background:#000; color:orange; padding:3px 10px; border-radius:4px; font-weight:bold; font-size:13px;">60–69 Orange</span>
                        <span style="background:#000; color:crimson; padding:3px 10px; border-radius:4px; font-weight:bold; font-size:13px;">50–59 Crimson</span>
                        <span style="background:#000; color:red; padding:3px 10px; border-radius:4px; font-weight:bold; font-size:13px;">&lt;50 Red</span>
                    </div>
                    <div style="color:#888; font-size:12px; margin-top:6px;">The player name header turns <b style="color:#b8860b;">gold</b> for OVR ≥ 80, <b style="color:#008b8b;">aqua</b> for OVR ≥ 70.</div>
                </div>

                <!-- Q5 -->
                <div style="margin-bottom:18px;">
                    <div style="font-weight:bold; color:#e67e22; margin-bottom:4px;">5. What does "(old)" mean next to a player's name?</div>
                    <div style="color:#444;">It means the player's stats have <b>not been updated</b> in that version — their data is carried over from a previous version unchanged.</div>
                </div>

                <!-- Q6 -->
                <div style="margin-bottom:18px;">
                    <div style="font-weight:bold; color:#e67e22; margin-bottom:4px;">6. How does Compare work?</div>
                    <div style="color:#444;">
                        Enter the <b>ID</b> and <b>version</b> for each player, then click <b>Compare</b>. You can compare 2 players by default.
                        Use <b>+ Add Player</b> to compare up to 4 players at once.<br/>
                        In the stat table, <span style="background:#d4edda; color:#155724; padding:1px 6px; border-radius:3px; font-weight:bold;">green</span> = highest value,
                        <span style="background:#f8d7da; color:#721c24; padding:1px 6px; border-radius:3px; font-weight:bold;">red</span> = lowest value.<br/>
                        A radar chart is shown when comparing exactly 2 players.
                    </div>
                </div>

                <!-- Q7 -->
                <div style="margin-bottom:18px;">
                    <div style="font-weight:bold; color:#e67e22; margin-bottom:4px;">7. How does Best XI work?</div>
                    <div style="color:#444;">
                        Choose a <b>formation</b>, then either:<br/>
                        • Click <b>Auto Pick</b> to automatically fill the best 11 players from the latest version.<br/>
                        • Click any <b>slot on the pitch</b> to manually search and assign a player to that position.<br/>
                        The <b>Team Rating</b> badge shows the average OVR of your current XI.<br/>
                        Click <b>Clear XI</b> to reset the pitch.
                    </div>
                </div>

                <!-- Q8 -->
                <div style="margin-bottom:18px;">
                    <div style="font-weight:bold; color:#e67e22; margin-bottom:4px;">8. How does Team Showcase work?</div>
                    <div style="color:#444;">
                        Select a <b>Nation</b> or <b>Club</b> from the dropdown. The app automatically builds the best possible XI
                        using the latest version data, with a bench of up to 8 substitutes.<br/>
                        Only nations/clubs with <b>19 or more players</b> in the latest version are available.
                    </div>
                </div>

                <!-- Q9 -->
                <div style="margin-bottom:18px;">
                    <div style="font-weight:bold; color:#e67e22; margin-bottom:4px;">9. What are Special Players?</div>
                    <div style="color:#444;">
                        Special Players are limited or event-based cards with boosted stats. They come in 4 types:
                        <span style="color:#555; font-weight:bold;">CLASSIC</span>,
                        <span style="color:purple; font-weight:bold;">STAR</span>,
                        <span style="color:blue; font-weight:bold;">CHAMPION</span>,
                        <span style="color:green; font-weight:bold;">TEAM</span>.
                        These are separate from regular player cards and are not version-specific.
                    </div>
                </div>

                <!-- Q10 -->
                <div style="margin-bottom:18px;">
                    <div style="font-weight:bold; color:#e67e22; margin-bottom:4px;">10. How do Favorites work?</div>
                    <div style="color:#444;">
                        Click the <b>★ star button</b> in any player detail panel to save that player to your Favorites list.
                        Favorites are stored in your browser's local storage — they persist between sessions but are
                        <b>device-specific</b> (not synced across devices). Up to 10 players are shown per page.
                    </div>
                </div>

                <!-- Q11 -->
                <div style="margin-bottom:18px;">
                    <div style="font-weight:bold; color:#e67e22; margin-bottom:4px;">11. Why can't I find a player?</div>
                    <div style="color:#444;">
                        Make sure you're searching in the correct <b>version</b>. A player may exist in one version but not another.
                        Also check that the <b>ID</b> is correct (max 4 digits). If searching by name, try using just the last name.
                    </div>
                </div>

                <!-- Q12 -->
                <div>
                    <div style="font-weight:bold; color:#e67e22; margin-bottom:4px;">12. How does Upgrade Sim work?</div>
                    <div style="color:#444;">
                        The <b>Upgrade Sim</b> tab lets you simulate upgrading a player's stats before committing in-game.<br/><br/>
                        <b>Loading a player:</b><br/>
                        • Click any player in your <b>Favorites</b> list on the left, <b>or</b><br/>
                        • Enter a player's <b>ID</b> + select a <b>version</b> on the right, then click <b>Load</b>.<br/><br/>
                        <b>Upgrading stats:</b><br/>
                        • Use the <b>▲ / ▼</b> arrows next to each stat to increase or decrease it.<br/>
                        • Stats cannot go below their original value or above <b>100</b>.<br/>
                        • Each player has a <b>max upgrade budget</b> of 82–87 points (varies by player).<br/>
                        • Some stats cost more points per level — <b>CON = ×2</b>, <b>STR = ×1.5</b>, <b>SPE/ACC/SHO = ×1.0</b>, <b>PAS = ×0.9</b>, <b>TAC = ×0.8</b>, <b>STA = ×0.5</b>.<br/><br/>
                        <b>OVR circle:</b><br/>
                        • The ring around the OVR number fills clockwise from 12 o'clock as you spend points.<br/>
                        • When the budget is fully used, the ring completes and OVR shows <b>base + 10</b>.<br/><br/>
                        Click <b>Reset</b> to restore all stats to their original values.<br/><br/>
                        <span style="background:#fff3cd;border:1px solid #ffc107;border-radius:4px;padding:3px 8px;font-size:12px;color:#856404;">
                            ⚠️ This is a <b>simulation only</b>. Actual in-game stats after upgrading may differ by ±1–2 points per attribute.
                        </span>
                    </div>
                </div>

            </div>
            `,
        },
    ],
});
