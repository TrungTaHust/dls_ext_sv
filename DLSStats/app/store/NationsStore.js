const nationsList = [
    "Albania", "Algeria", "Andorra", "Angola", "Antigua & Barbuda", "Argentina", "Armenia", "Australia", 
    "Austria", "Belarus", "Belgium", "Benin", "Bermuda", "Bosnia & Herzegovina", "Brazil", "Bulgaria", 
    "Burkina Faso", "Burundi", "Cameroon", "Canada", "Cape Verde", "Central Africa", "Chile", "Colombia",
    "Congo", "Costa Rica", "Croatia", "Cuba", "Curacao", "Cyprus", "Czech Republic", "DR Congo", 
    "Denmark", "Dominican Republic", "Ecuador", "Egypt", "England", "Equatorial Guinea", "Estonia",
    "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada",
    "Guadeloupe", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary",
    "Iceland", "Indonesia", "Irag", "Iran", "Ireland", "Israel", "Italy", "Ivory Coast", "Jamaica",
    "Japan", "Jordan", "Kenya", "Kosovo", "Liberia", "Lithuania", "Luxembourg", "Lybia", "Mali", "Malta",
    "Mexico", "Montenegro", "Morocco", "Mozambique", "Namibia", "Netherlands", "New Zealand", "Nigeria",
    "North Macedonia", "North. Ireland", "Norway", "Panama", "Paraguay", "Peru", "Philippines", "Poland",
    "Portugal", "Romania", "Russia", "Saint Kitts and Nevis", "Saudi Arabia", "Scotland", "Senegal",
    "Serbia", "Sierra Leone", "Slovakia", "Slovenia", "South Africa", "South Korea", "Spain", 
    "St. Kitts & Nevis", "St. Lucia", "Suriname", "Sweden", "Switzerland", "Syria", "Togo",
    "Trinidad & Tobago", "Tunisia", "Turkey", "UAE", "USA", "Uganda", "Ukraine", "Uruguay", "Uzbekistan",
    "Venezuela", "Wales", "Zambia", "Zimbabwe"
]

Ext.define('DLSStats.store.NationsStore', {
    extend: 'Ext.data.Store',
    alias: 'store.nationsstore',

    fields: ['name'],
    data: nationsList.map(function (name) {
        return { name: name };
    })
});
