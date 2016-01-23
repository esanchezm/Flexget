(function () {
  'use strict';

  var logModule = angular.module('flexget.plugins.log', ['ui.grid', 'ui.grid.autoResize', 'ui.grid.autoScroll']);
  registerModule(logModule);

  logModule.run(function(route, sideNav, toolBar, $state) {
    route.register('log', '/log', 'logController', 'plugins/log/log.tmpl.html');
    sideNav.register('/log', 'Log', 'fa fa-file-text-o', 128);
    toolBar.registerButton('Log', 'fa fa-file-text-o', function(){$state.go('log')});
  });

})();