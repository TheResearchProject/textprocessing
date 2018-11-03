var response_content;

'use strict';

angular.module('myApp', [
  'ngRoute',
  'ngUpload',
  'ngMaterial',
  'myApp.version'
]).
controller('DeController', ['$scope', 
                            '$http', 
                            '$document', 
                            '$mdDialog', 
                            function($scope, 
                                     $http, 
                                     $document,
                                     $mdDialog){
  $scope.language = 'english';
  $scope.upload_option = 'text_field';
  $scope.stopwords = 'our_stopwords';
  $scope.stemmer = 'porter';
  $scope.lemmatizer = 'lemmatizer_on';
  $scope.error_text = "";
  $scope.callback_ok = false;
  $scope.results = [];
  $scope.resulting_text = "";
  $scope.input_text_word_count = 0;
  $scope.input_text_char_count = 0;
  $scope.output_text_word_count = 0;
  $scope.output_text_char_count = 0;
  
  $scope.callback = function(content) {
    console.log(content);
    response_content = content;
    if (content.status == 'success') {
      $scope.callback_ok = true;
      $scope.results = content.sorteddict;
      $scope.resulting_text = content.resulting_text;
      $scope.input_text_word_count = content.input_text_word_count;
      $scope.input_text_char_count = content.input_text_char_count;
      $scope.output_text_word_count = content.output_text_word_count;
      $scope.output_text_char_count = content.resulting_text.length;
      chart1Options.xAxis.categories = content.words;
      chart1Options.series[0].data = content.percentages;
      Highcharts.chart('chart1', chart1Options);
      chart2Options.xAxis.categories = content.words;
      chart2Options.series[0].data = content.frequencies;
      chart2Options.series[1].data = content.acum_perc_list;
      Highcharts.chart('chart2', chart2Options);
      chart3Options.series[0].data = content.logarithms;
      chart3Options.series[1].data = [
        content.regression_line.start, 
        content.regression_line.end
      ];
      Highcharts.chart('chart3', chart3Options);
      $scope.error_text = ""; 
      WordCloud(document.getElementById('word_cloud'), { 
        list: content.word_cloud,
        weightFactor: 4
      } );
    }
    else{
      $scope.results = [];
      $scope.error_text = content.message; 
    }
  };
  
  $scope.onChangeLanguage = function(){
    if ($scope.language == 'dutch'){
      $scope.stemmer = "snowball";
    }
  };
  
  $scope.saveTextResult = function(){
    if ($scope.resulting_text != ""){
      var blob = new Blob([$scope.resulting_text], {type: "text/plain;charset=utf-8"});
      saveAs(blob, "result_text.txt");
    }
    else {
      $mdDialog.show(
        $mdDialog.alert()
          .clickOutsideToClose(true)
          .title('No result text.')
          .textContent('No result text available. Either the returning result was empty or you didn\'t click the "Perform" button.')
          .ariaLabel('Alert Dialog Demo')
          .ok('OK')
      );      
    }
  };
  
}]);

var chart1Options = {
    title: {
        text: 'Word frequency',
        x: -20 //center
    },
    tooltip: {
      valueSuffix: ' %'
    },
    xAxis: {
        title: {
          text: 'Word'
        },
        categories: []
    },
    yAxis: [{
        title: {
            text: 'Frequency'
        },
        plotLines: [{
            value: 0,
            width: 1,
            color: '#808080'
        }]
    },{
        title: {
            text: 'Accumulated %'
        },
        plotLines: [{
            value: 0,
            width: 1,
            color: '#808080'
        }]
    }],
    series: [{
        name: 'Frequency',
        data: []
    }]
};

var chart2Options = {
    title: {
        text: 'Accumulated word frequency',
        x: -20 //center
    },
    xAxis: {
        title: {
          text: 'Word'
        },
        categories: []
    },
    yAxis: {
        title: {
            text: 'Frequency'
        },
        plotLines: [{
            value: 0,
            width: 1,
            color: '#808080'
        }]
    },
    series: [{
        type: 'column',
        name: 'Frequency',
        data: []
    },
    {
        type: 'line',
        name: 'Accumulated %',
        data: []
    }]
};

var chart3Options = {
    title: {
        text: 'log(rank) - log(frequency)',
        x: -20 //center
    },
    series: [{
        type: 'scatter',
        name: 'log(rank) - log(frequency)',
        data: []
    },
    {
        type: 'line',
        name: 'Regression Line',
        data: [],
        marker: {
            enabled: false
        },
        states: {
            hover: {
                lineWidth: 0
            }
        },
        enableMouseTracking: false
    }]
};
