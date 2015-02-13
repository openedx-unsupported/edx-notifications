describe("CounterIconView", function(){


    beforeEach(function(){
        jasmine.Ajax.install();
    });

    afterEach(function() {
      jasmine.Ajax.uninstall();
    });

    it("counter view model url is set successfully", function(){
         $('body').append('<div id="edx_notification_container" />');
        this.counter_view = new CounterIconView({
            el: $("#edx_notification_container"),
            pane_el: $("#edx_notification_pane"),

            endpoints: {
                unread_notification_count: "initialize_count",
                user_notifications: "",
                renderer_templates_urls: ""
            },
            view_templates: {
                notification_icon: "edx_notifications/templates/notification_icon.html",
                notification_pane: "edx_notifications/templates/notification_pane.html"
            }
        });
        expect(this.counter_view.model.url).toBe("initialize_count")
    });
});
