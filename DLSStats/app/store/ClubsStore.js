const clubsList = [
    'AC Milan', 'Aberdeen', 'Ajax', 'Alaves', 'Alkmaar', 'Almeria', 'Angers', 'Arouca', 'Arsenal',
    'Aston Villa', 'Atalanta', 'Athletic Bilbao', 'Atletico Madrid', 'Auxerre', 'Aves', 'Azores',
    'Barcelona', 'Barcelos', 'Benfica', 'Birmingham', 'Blackburn', 'Boavista', 'Bologna', 'Bournemouth',
    'Braga', 'Breda', 'Brentford', 'Brest', 'Brighton', 'Bristol', 'Burnley', 'Cadiz', 'Cagliari',
    'Cardiff', 'Casa P', 'Celta Vigo', 'Celtic', 'Chaves', 'Chelsea', 'Clermont-Ferrand', 'Como',
    'Cornella', 'Coventry', 'Cremonese', 'Crystal Palace', 'Derby', 'Dundee', 'Dundee U', 'E Amadora',
    'Eibar', 'Elche', 'Empoli', 'Estoril', 'Everton', 'Famalicao', 'Farense', 'Feyenoord', 'Fiorentina',
    'Frosinone', 'Fulham', 'GA Eagles', 'Genoa', 'Getafe', 'Girona', 'Glasgow R', 'Granada', 'Guimaraes',
    'Hearts', 'Heerenveen', 'Heracles Almelo', 'Hibernian', 'Huddersfield', 'Hull', 'Inter Milan',
    'Ipswich', 'Juventus', 'Kilmarnock', 'Las Palmas', 'Lazio', 'Le Havre', 'Lecce', 'Leeds', 'Leganes',
    'Leicester', 'Lens', 'Lille', 'Liverpool', 'Livingston', 'Lorient', 'Luton', 'Lyon', 'Mallorca',
    'Man City', 'Man United', 'Marseille', 'Metz', 'Middlesbrough', 'Millwall', 'Monaco', 'Montpellier',
    'Monza', 'Moreirense', 'Motherwell', 'N Funchal', 'Nantes', 'Napoli', 'Newcastle', 'Nice',
    'Nijmegen', 'Norwich', 'Nottingham', 'Osasuna', 'Oxford', 'PSV', 'Paris SG', 'Parma', 'Plymouth',
    'Portimao', 'Porto', 'Portsmouth', 'Preston', 'Queens Park R', 'Rayo Vallecano', 'Real Betis',
    'Real Madrid', 'Real Sociedad', 'Reims', 'Rennes', 'Rio Ave', 'Roma', 'Ross C', 'Rotherham',
    'Rotterdam', 'S Johnstone', 'S Lisbon', 'S Mirren', 'Saint-Etienne', 'Salernitana', 'Sassuolo',
    'Sevilla', 'Sheffield United', 'Sheffield W', 'Sittard', 'Southampton', 'Stoke', 'Strasbourg',
    'Sunderland', 'Swansea', 'Torino', 'Tottenham', 'Toulouse', 'Twente', 'Udinese', 'Utrecht',
    'V Arnhem', 'Valencia', 'Valladolid', 'Venezia', 'Verona', 'Villareal', 'Vitoria', 'Vizela',
    'Waalwijk', 'Watford', 'West Bromwich', 'West Ham', 'Wigan', 'Willem', 'Wolves', 'Zwolle'
];

Ext.define('DLSStats.store.ClubsStore', {
    extend: 'Ext.data.Store',
    alias: 'store.clubsstore',

    fields: ['name'],
    data: clubsList.map(function (name) {
        return { name: name };
    })
});
