angular.module('alkivi_archive', []).service('eventNotifyer', [ '$rootScope', '$log', '$timeout',  function ($rootScope, $log, $timeout) {
	this.events  = [];

//    this.startLoading = function() { $rootScope.$broadcast('startLoading'); $log.log('startLoading'); };
//    this.stopLoading  = function() { $rootScope.$broadcast('stopLoading'); $log.log('stopLoading'); };

	this.addError   = function(error)   { this.events.push({ type: 'error', msg : error }) };
	this.addSuccess = function(success) { 
        this.events.push({ type: 'success', msg : success }) 
        // TODO : remove it automatically after x seconds ??
    };

    this.reset = function() { this.events = [] };

}]).controller('EventCtrl', ['$scope', '$log', 'eventNotifyer', function($scope, $log, $eventNotifyer) {
	$scope.events  = $eventNotifyer.events;

	$scope.closeEvent = function(index) {
		$scope.events.splice(index, 1);
	};

    $scope.resetEvents = function() { $eventNotifyer.events = []; $scope.events = $eventNotifyer.events; };

}]).factory('HttpInterceptor', ['$q', 'eventNotifyer',  function($q, $eventNotifyer) {
    'use strict';
    return function (promise) {
        return promise.then(function (response) {
            if(response.headers() && response.headers()['content-type'] === 'application/json') {
				if(!response.data.status) { // other call
					return response;
				}else  if(response.data.status < 200) { // ok
                    // if confirm message, then print it   
                     if(response.data.confirm)
                     {
						 $eventNotifyer.addSuccess( response.data.confirm );
                     }
                    // return all data
                    return response;
                }else{ 
                    // error add to eventNotifyer only if msg is defined
                    if(response.data.msg) {
                        var msg = response.data.msg;
                        var error = 'Error on ' + response.config.method + ' ' + response.config.url + ' : ' + msg;
                        $eventNotifyer.addError ( error );
                    }
                    //and reject
                    return $q.reject(response);
                };
            }else{
                return response;
            }
        }, function (response) { // error low level
			// if json, then error
			var error  = 'Internal error on ' + response.config.method + ' ' + response.config.url;
			$eventNotifyer.addError( error );
			return $q.reject(response);
        });
    };
}]).config([ '$routeProvider', '$httpProvider',  function ($routeProvider, $httpProvider, $log ) {


    // to set the loading easily
    $httpProvider.defaults.transformRequest.push(function(data) {
        var $injector  = angular.element('#rootBody').injector();
        var $rootScope = $injector.get('$rootScope');
        $rootScope.$broadcast('startLoading');
        return data;
    });

    $httpProvider.defaults.transformResponse.push(function(data) {
        var $injector  = angular.element('#rootBody').injector();
        var $rootScope = $injector.get('$rootScope');
        $rootScope.$broadcast('stopLoading');
        return data;
    });

    // to handle correctly error
    $httpProvider.responseInterceptors.push('HttpInterceptor');


    // routes
    $routeProvider.when('/pcaList',{
        templateUrl : 'views/pcaList.html',
        controller  : PcaListCtrl
    }).when('/search',{
        templateUrl : 'views/search.html',
        controller  : SearchCtrl
    }).when('/pca/:pcaId',{
        templateUrl : 'views/pca.html',
        controller  : PcaCtrl
    }).when('/session/:sessionId',{
        templateUrl : 'views/session.html',
        controller  : SessionCtrl
    }).otherwise({
        redirectTo: '/pcaList'
    });
}]);
