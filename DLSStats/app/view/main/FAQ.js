Ext.define("DLSStats.view.main.FAQ", {
    extend: "Ext.container.Container",
    xtype: "dls-faq",

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

    layout: {
        type: "vbox",
        align: "stretch",
        style: {
            backgroundColor: "rgba(0, 0, 0, 0.5)",
        },
    },

    items: [
        {
            xtype: "container",
            margin: "0 0 10 0",
            html: "<b>1. Where to get ID?</b><br/>- In every player's details",
        },
        {
            xtype: "container",
            margin: "0 0 10 0",
            html: `
        <b>2. What does each version mean?</b><br/>
        - 20231 = During mid 2023<br/>
        - 20241 = 2023 December<br/>
        - 20242 = 2024 May<br/>
        - 20251 = 2024 December<br/>
        - 20252 = 2025 February<br/>
        - 20253 = 2025 June
      `,
        },
    ],
});
