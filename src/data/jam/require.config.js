var jam = {
    "packages": [
        {
            "name": "flot",
            "location": "jam/flot",
            "main": "jquery.flot.js"
        },
        {
            "name": "jquery",
            "location": "jam/jquery",
            "main": "dist/jquery.js"
        }
    ],
    "version": "0.2.17",
    "shim": {
        "flot": {
            "exports": "jQuery",
            "deps": [
                "jquery"
            ]
        }
    }
};

if (typeof require !== "undefined" && require.config) {
    require.config({
    "packages": [
        {
            "name": "flot",
            "location": "jam/flot",
            "main": "jquery.flot.js"
        },
        {
            "name": "jquery",
            "location": "jam/jquery",
            "main": "dist/jquery.js"
        }
    ],
    "shim": {
        "flot": {
            "exports": "jQuery",
            "deps": [
                "jquery"
            ]
        }
    }
});
}
else {
    var require = {
    "packages": [
        {
            "name": "flot",
            "location": "jam/flot",
            "main": "jquery.flot.js"
        },
        {
            "name": "jquery",
            "location": "jam/jquery",
            "main": "dist/jquery.js"
        }
    ],
    "shim": {
        "flot": {
            "exports": "jQuery",
            "deps": [
                "jquery"
            ]
        }
    }
};
}

if (typeof exports !== "undefined" && typeof module !== "undefined") {
    module.exports = jam;
}