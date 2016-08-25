define([
    'base/js/namespace',
    'notebook/js/actions',
], function(
    Jupyter,
    actions
) {
  var actions = new actions.init();

  function load_ipython_extension() {
    var DojoClock = {
      seconds: 300,
      default: 300,
      users: [],
      startTime: null,
      timer_running: false,
      registering: false,
      interfaces: [],

      secToMMSS: function (sec) {
        var minutes = Math.floor(sec / 60);
        var seconds = sec - (minutes * 60);
        if (minutes < 10) { minutes = "0" + minutes; }
        if (seconds < 10) { seconds = "0" + seconds; }
        return minutes + ":" + seconds;
      },

      display: function () {
        var self = this;
        self.interfaces.forEach(function(view){
          view.updateTime(self.secToMMSS(self.seconds));
        });
      },

      start: function () {
        var self = this;
        self.timer_running = true;
        self.interfaces.forEach(function(view){
          view.updatePlayPause(self.timer_running);
        });
        this.interval = setInterval(function () {
          self.display();
          if (self.seconds == 0) {
            self.pause();
            if (self.startTime == null) {
              alert("Time is up. Click ok to restart timer");
            } else {
              var newTime = new Date();
              self.users.push([self.startTime, newTime, self.pilot, self.copilot]);
              self.pilot = self.copilot;
              self.copilot = prompt("Time is up. Who is the new copilot?");
              self.startTime = new Date();
            }
            self.seconds = self.default;
            self.start();
          } else {
            self.seconds--;
          }
          self.timer_running = true;
          self.interfaces.forEach(function(view){
            view.updatePlayPause(self.timer_running);
          });

        }, 1000);
        self.interfaces.forEach(function(view){
          view.updateInterval(this.interval);
        });
      },

      pause: function () {
        var self = this;
        self.timer_running = false;
        self.interfaces.forEach(function(view){
          view.updatePlayPause(self.timer_running);
        });
        clearInterval(this.interval);
        delete this.interval;
      },

      resume: function () {
        if (!this.interval) this.start();
      },

      reset: function () {
        var self = this;
        self.seconds = self.default;
        self.display();
        self.pause();
      },

      startRegistering: function () {
        var self = this;
        self.registering = true;
        self.interfaces.forEach(function(view){
          view.updateRegistering(self.registering);
        });
        self.pilot = prompt("Who is the pilot?");
        self.copilot = prompt("Who is the co-pilot?");
        self.startTime = new Date();
      },

      stopRegistering: function () {
        var self = this;
        self.registering = false;
        self.interfaces.forEach(function(view){
          view.updateRegistering(self.registering);
        });
        self.users.push([self.startTime, new Date(), self.pilot, self.copilot]);
        self.startTime = null;
      },

      peopleLog: function () {
        var self = this;
        var result = "";
        self.users.forEach(function(value) {
          result += "- " + value[0].toLocaleTimeString() + " -> " + value[1].toLocaleTimeString();
          result += " = " + value[2] + ", " + value[3] + "\r\n";
        });
        if (self.startTime != null) {
          result += "- " + self.startTime.toLocaleTimeString() + " -> " + (new Date()).toLocaleTimeString();
          result += " = " + self.pilot + ", " + self.copilot + "\r\n";
        }
        var cell = Jupyter.notebook.insert_cell_at_bottom("markdown");
        cell.set_text(result.slice(0,-2));
      },

      configure: function () {
        var self = this;
        var time = prompt("New time in seconds", self.default);
        self.default = time;
        self.reset();
      }
    };
    var prefix = 'jupyter-dojo';
    var view = {
      eyeb: "#"+prefix+" button[data-jupyter-action='"+prefix+":dojo-time']",
      eye: "#"+prefix+" button[data-jupyter-action='"+prefix+":dojo-time'] i",
      play: "#"+prefix+" button[data-jupyter-action='"+prefix+":dojo-play-pause'] i",
      register: "#"+prefix+" button[data-jupyter-action='"+prefix+":dojo-register-log'] i",
      interval: "dojo-timer-interval",
      timer: "dojo-timer-time",
      mouseOver: false,

      viewText: function() {
        var self = this;
        if ($(self.eye).hasClass("fa-eye") ||
            $(self.play).hasClass("fa-play") ||
            self.mouseOver) {
          $("#" + self.timer).css("color", "black");
        } else {
          $("#" + self.timer).css("color", "transparent");
        }
      },

      updatePlayPause: function(running) {
        var self = this;
        var action = actions._actions[prefix + ":" + "dojo-play-pause"];
        if (!running) {
          action.icon = "fa-play";
          $(self.play).removeClass("fa-pause");
        } else {
          action.icon = "fa-pause";
          $(self.play).removeClass("fa-play");
        }
        $(self.play).addClass(action.icon);
        self.viewText();
      },

      updateTime: function(time) {
        var self = this;
        $("#" + self.timer).text(time);
      },

      updateInterval: function(interval) {
        var self = this;
        $("#" + self.interval).text(interval);
      },

      updateRegistering: function(registering) {
        var self = this;
        var action = actions._actions[prefix + ":" + "dojo-register-log"];
        if (registering) {
          action.icon = "fa-times";
          action.help = "stop logging people";
          $(self.register).removeClass("fa-user");
        } else {
          action.icon = "fa-user";
          action.help = "log people";
          $(self.register).removeClass("fa-times");
        }
        $(self.register).addClass(action.icon);
        $(self.register).prop("title", action.help);
      },

      cleanup: function() {
        var self = this;
        var interval = parseInt($("#" + self.interval).text());
        clearInterval(interval);
      },

      init: function() {
        var self = this;
        $(self.eye).after(
          '<span id="' + self.interval + '" ' +
            'style="margin: 0 5px; display: none;"></span>' +
          '<span id="' + self.timer + '" ' +
            'style="margin: 0 5px; color:black;">05:00</span>');
        $(self.eyeb).hover(function(e) {
          if ($(self.eye).hasClass("fa-eye-slash")) {
            self.mouseOver = e.type === "mouseenter";
            self.viewText();
          }
        }, function(e) {
          self.mouseOver = false;
          self.viewText();
        });
      },

      toggle_eye: function() {
        var self = this;
        if ($(self.eye).hasClass("fa-eye-slash")) {
          $(self.eye).removeClass("fa-eye-slash");
          $(self.eye).addClass("fa-eye");
        } else {
          $(self.eye).addClass("fa-eye-slash");
          $(self.eye).removeClass("fa-eye");
        }
        self.viewText();
      }
    };

    if ($("#" + prefix).length) {
      return;
     // interface.cleanup();
     // $("#" + prefix).remove();
    }

    var dojo_actions = [
      {
        name: 'dojo-create',
        icon: 'fa-group',
        help    : 'create dojo',
        help_index : 'zz',
        handler : function () {
            var fn = prompt("Function Name?");
            Jupyter.notebook.insert_cell_below().set_text("%%unittest -p 1\nassert "+fn+"() == 0");
            Jupyter.notebook.insert_cell_below().set_text("def "+fn+"():\n    pass");
            Jupyter.notebook.insert_cell_below().set_text("%load_ext ipython_unittest.dojo");
        }
      },
      {
        name: 'dojo-list-log',
        icon: 'fa-list',
        help    : 'copy people log to new cell',
        help_index : 'zz',
        handler : function(e){DojoClock.peopleLog()}
      },
      {
        name: 'dojo-register-log',
        icon: 'fa-user',
        help    : 'log people',
        help_index : 'zz',
        handler : function(e){
          if (DojoClock.registering) {
            DojoClock.stopRegistering();
          } else {
            DojoClock.startRegistering();
          }
        }
      },
      {
        name: 'dojo-play-pause',
        icon: 'fa-play',
        help    : 'play/pause time',
        help_index : 'zz',
        handler : function(e){
          DojoClock.timer_running ? DojoClock.pause() : DojoClock.resume();
        }
      },
      {
        name: 'dojo-time',
        icon: 'fa-eye-slash',
        help    : 'toggle timer',
        help_index : 'zz',
        handler : function(){view.toggle_eye()}
      },
      {
        name: 'dojo-reset-time',
        icon: 'fa-refresh',
        help    : 'reset time',
        help_index : 'zz',
        handler : function(){DojoClock.reset()}
      },
      {
        name: 'dojo-configure-time',
        icon: 'fa-wrench',
        help    : 'configure time',
        help_index : 'zz',
        handler : function(){DojoClock.configure()}
      }
    ];

    var group = []
    dojo_actions.forEach(function(action) {
      action.full_name = actions.register(action, action.name, prefix);
      group.push(action.full_name);
    });

    Jupyter.toolbar.add_buttons_group(group, prefix);
    view.init();
    DojoClock.interfaces.push(view);
  }
  return {
    load_ipython_extension: load_ipython_extension
  };

});
