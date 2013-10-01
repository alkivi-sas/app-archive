function RootCtrl($scope, $log, $routeParams, $http, $window, $location, $filter ) {

    $scope.fixLocation = function(url, $event) {
        $location.url(url);

        if($event) { // might be called internally
            $event.preventDefault()
        }
    };

}

function SearchCtrl($scope, $routeParams, $http, $log, $location, eventNotifyer) {
    $scope.fileName = null;
    $scope.files    = [];

    $scope.search = function() {
        $http.get('cgi/dispatcher.py', { params: { action: 'searchFiles', fileName: $scope.fileName } }).success(function(data) {
            $scope.files = data.value;
        });
    };
}

function PcaListCtrl($scope, $routeParams, $http, $log, $location, eventNotifyer) {
    $scope.pcaList = null;

    $scope.getPcaList = function() {
        $http.get('cgi/dispatcher.py', { params: { action: 'pcaList' } }).success(function(data) {
            $scope.pcaList = data.value;
        });
    };

    $scope.getPcaList()
}

function PcaCtrl($scope, $routeParams, $http, $log, $location, eventNotifyer) {
    $scope.pcaId = null

        if($routeParams.pcaId) {
            $scope.pcaId = $routeParams.pcaId;
        }else{
            eventNotifyer.addError('No pcaId');
        }    

    $scope.getPcaSessions = function() {
        $http.get('cgi/dispatcher.py', { params: { action: 'sessionList', pcaId: $scope.pcaId } } ).success(function(data) {
            $scope.sessionList = data.value;
        });
    };

    $scope.getPcaSessions()
}

function SessionCtrl($scope, $routeParams, $http, $log, $location, eventNotifyer) {
    $scope.session = null

        if($routeParams.sessionId) {
            $scope.sessionId = $routeParams.sessionId;
        }else{
            eventNotifyer.addError('No session Id');
        }    

    $scope.getSessionFiles = function() {
        $http.get('cgi/dispatcher.py', { params: { action: 'fileList', sessionId: $scope.sessionId } } ).success(function(data) {
            $scope.fileList = data.value;
        });
    };

    $scope.getSessionFiles()
}
