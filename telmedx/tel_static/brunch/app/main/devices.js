const $ = require('jquery');

module.exports = {
    $el: null,

    init: function (el) {
        this.$el = $(el);

        if (this.$el) {
            this.bindUiActions();
        }
    },

    bindUiActions: function () {
        const context = this,
            $filter = context.$el.find("#filter");
        let count = 0;

        this.$el.find('.device-item').click((e) => {
            window.location.href = $(e.currentTarget).data('link');
        });

        if ($filter.length !== 0) {
            $filter.keyup(() => {
                count = 0;
                $("#dev-table tr").each(function() {
                    if ($(this).find("a:first").text().search(new RegExp($filter.val(), "i")) < 0) {
                        $(this).addClass("hidden");
                    } else {
                        $(this).removeClass("hidden");
                        count++;
                    }
                });
                $("#filter-count").text(count);
            });
        }
    }
};

