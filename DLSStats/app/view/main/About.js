Ext.define("DLSStats.view.main.About", {
    extend: "Ext.container.Container",
    xtype: "about",

    style: {
        backgroundImage: 'url("./resources/background.jpg")',
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        padding: "20px",
        color: "#fff",
        fontFamily: "Arial, sans-serif",
        fontSize: "14px",
    },

    items: {
        xtype: "container",
        style: {
            backgroundColor: "rgba(0, 0, 0, 0.5)",
        },

        html: `        
        <p>My contact:</p>
        <ul>
            <li><b>Email:</b> <a href="mailto:trungta.hust@gmail.com" style="color:#aaddff;">trungta.hust@gmail.com</a></li>
            <li><b>Facebook:</b> <a href="https://facebook.com/hieu.tatrung.7" target="_blank" style="color:#aaddff;">facebook.com/hieu.tatrung.7</a></li>
            <li><b>X (Twitter):</b> <a href="https://x.com/TrungTa4970" target="_blank" style="color:#aaddff;">x.com/TrungTa4970</a></li>
        </ul>
        <p>This website is free for everyone to use, but any support is warmly appreciated!</p>
        `,
    },
});
