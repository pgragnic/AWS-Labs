var ViewModel = function () {
    var self = this;
    self.url = window.location.href
    self.searchTerm = ko.observable();
    self.searchHits = ko.observableArray([]);
    self.totalHits = ko.observable(0);
    self.chapterCount = ko.observable(0);
    self.totalScore = ko.observable(0);
    var apigateway = "https://6fksxo2fb1.execute-api.us-east-1.amazonaws.com";
    var tableVis = "container overflow-auto contentbox w-75";
    
    async function queryEs(url = apigateway+'?query='+String(self.searchTerm())) {
        const response = await fetch(url, {
          cache: 'no-cache',
        });
        return response.json();
      }

    self.frankenSearch = function() {
        queryEs()
          .then(data => {
              self.searchHits(data.hits);
              self.totalHits(data.total_hits);
              self.chapterCount(data.chapter_count);
              self.totalScore(data.total_score);
          });        
    };
  };

ko.applyBindings(new ViewModel());