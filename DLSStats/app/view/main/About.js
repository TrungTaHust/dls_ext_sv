Ext.define("DLSStats.view.main.About", {
    extend: "Ext.container.Container",
    xtype: "about",

    layout: { type: "vbox", align: "center", pack: "center" },

    style: {
        backgroundImage: 'url("./resources/background.jpg")',
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
    },

    items: [
        {
            xtype: "component",
            margin: 20,
            html: `
            <div style="
                background: rgba(245,245,245,0.97);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 12px;
                padding: 32px 40px;
                max-width: 480px;
                color: #222;
                font-family: Arial, sans-serif;
                font-size: 14px;
                line-height: 1.7;
                box-shadow: 0 4px 24px rgba(0,0,0,0.3);
            ">
                <div style="text-align:center; margin-bottom: 20px;">
                    <div style="font-size:28px; font-weight:bold; letter-spacing:1px; color:#222;">DLS Stats</div>
                    <div style="color:#888; font-size:12px; margin-top:4px;">Dream League Soccer Player Database</div>
                </div>

                <hr style="border:none; border-top:1px solid #ddd; margin: 16px 0;"/>

                <div style="margin-bottom: 16px;">
                    <div style="color:#999; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">Contact</div>
                    <div style="margin-bottom:6px;">
                        📧 <a href="mailto:trungta.hust@gmail.com" style="color:#2980b9; text-decoration:none;">trungta.hust@gmail.com</a>
                    </div>
                    <div style="margin-bottom:6px;">
                        📘 <a href="https://facebook.com/hieu.tatrung.7" target="_blank" style="color:#2980b9; text-decoration:none;">facebook.com/hieu.tatrung.7</a>
                    </div>
                    <div>
                        🐦 <a href="https://x.com/TrungTa4970" target="_blank" style="color:#2980b9; text-decoration:none;">x.com/TrungTa4970</a>
                    </div>
                </div>

                <hr style="border:none; border-top:1px solid #ddd; margin: 16px 0;"/>

                <div style="text-align:center; color:#555; font-size:13px;">
                    This website is free for everyone to use.<br/>
                    Any support is warmly appreciated! 🙏
                </div>
            </div>
            `,
        },
    ],
});
