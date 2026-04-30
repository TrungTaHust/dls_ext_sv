Ext.define('DLSStats.Application', {
    extend: 'Ext.app.Application',

    name: 'DLSStats',

    quickTips: false,
    platformConfig: {
        desktop: {
            quickTips: true
        }
    },

    searchPlayersByCriteria: function (criteria, nameTerm) {
        var playerStore = Ext.getStore('playerstore');
        if (!playerStore) {
            console.error('Player store not found');
            return [];
        }

        nameTerm = nameTerm ? nameTerm.toLowerCase() : null;

        var filteredRecords = playerStore.queryBy(function (record) {
            for (var key in criteria) {
                var value = record.get(key);
                if (value == null) return false;

                var criteriaValue = criteria[key];
                if (typeof value === 'number') {
                    if (value !== parseInt(criteriaValue)) return false;
                } else {
                    if (String(value).toLowerCase().indexOf(String(criteriaValue).toLowerCase()) === -1)
                        return false;
                }
            }

            if (nameTerm) {
                var fullName = (record.get('fname') + record.get('lname')).toLowerCase();
                if (fullName.indexOf(nameTerm) === -1) return false;
            }

            return true;
        });

        return filteredRecords.getRange();
    }
});


