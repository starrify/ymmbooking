!function ($) {
    "use strict";

    var PopoverEx = function (element, options) {
        this.init('popoverex', element, options);
    }
    
    PopoverEx.prototype = $.extend({}, $.fn.popover.Constructor.prototype, {
        constructor : PopoverEx,
        
        inReserveState: function() {
            var hoverReserves = this.options.hoverReserve.split(' ');
            if(hoverReserves.indexOf(this.hoverState) == -1)
                return false;
            else
                return true;
        },
        
        triggerHover: function() {
            var triggers = this.options.trigger.split(' ');
            return (triggers.indexOf('hover') != -1);
        },

        enterPopover: function (e) {
            this.hoverState = 'in_popover'
        },
        
        leavePopover: function (e) {
            if (this.timeout) clearTimeout(this.timeout);
            if (!this.options.delay || !this.options.delay.hide) return this.hide();
            this.hoverState = 'out';

            var self = this;
            this.timeout = setTimeout(function() {
                if(!self.inReserveState()) self.hide();
            }, this.options.delay.hide);
        },

        leave: function (e) {
            var self = $(e.currentTarget)[this.type](this._options).data(this.type)

            if (this.timeout) clearTimeout(this.timeout)
            if (!self.options.delay || !self.options.delay.hide) return self.hide()

            self.hoverState = 'out'
            this.timeout = setTimeout(function() {
                if (!self.inReserveState()) self.hide()
            }, self.options.delay.hide)
        },

        init: function(type, element, options) {
            $(element).off('.' + this.type);
            $.fn.popover.Constructor.prototype.init.call(this, type, element, options);
            
            this.tip().off('.' + this.type);
            if(this.triggerHover()) {
                this.tip().on('mouseenter.' + this.type, $.proxy(this.enterPopover, this));
                this.tip().on('mouseleave.' + this.type, $.proxy(this.leavePopover, this));
            }
            if(this.options['popover_click']) {
                this.tip().on('click.' + this.type, {ele: this.$element, pop: this.tip()}, this.options['popover_click']);
            }

//            this.visible = false; //???
        },

        show: function() {
            if(this.pinned) return this;

            $.fn.popover.Constructor.prototype.show.call(this);
            this.visible = true;
            return this;
        },

        hide: function() {
            if(this.pinned) return this;

            $.fn.popover.Constructor.prototype.hide.call(this);
            this.visible = false;
            return this;
        },
        
        destroy: function () {
            this.hide().$element.off('.' + this.type).removeData(this.type)
        },

        pin: function() {
            if(this.triggerHover() && this.visible) {
                this.pinned = true;
            }
        },

        unpin: function() {
            if(this.triggerHover() && this.visible) {
                this.pinned = false;
                if(!this.inReserveState())
                    this.hide();
            }
        },

        togglePin: function() {
            if(this.pinned)
                this.unpin();
            else
                this.pin();
        },
    });

    $.fn.popoverex = function (option) {
        return this.each(function () {
            var $this = $(this)
                , data = $this.data('popoverex')
                , options = typeof option == 'object' && option;
            if (typeof option == 'string') {
                if (!data) $this.data('popoverex', (data = new PopoverEx(this, options)));
                data[option].call(data);
            } else {
                if (!data) $this.data('popoverex', (data = new PopoverEx(this, options)));
                else {
                    var modified = false;
                    for(var key in options) {
                        console.log(data.options[key], options[key]);
                        if(JSON.stringify(data.options[key]) != JSON.stringify(options[key])) {
                            data.options[key] = options[key];
                            console.log('different key', key);
                            modified = true;
                        }
                    }
                    if(modified) {
                        data.init(data.type, this, data.options);
                    }
                }
            }
        });
    }
    $.fn.popoverex.Constructor = PopoverEx;
    $.fn.popoverex.defaults = $.extend({}, $.fn.popover.defaults, {
        hoverReserve: 'in',
    });
}(window.jQuery);
