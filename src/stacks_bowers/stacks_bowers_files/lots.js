WebModule.controller('LotsController',
        ['$scope', 'WMService', 'LotService', 'LotViewState', 'AuctionService', 'Auction', 'AddressService', 'FilterService', '$location', '$http', '$filter', '$timeout', '$rootScope',
    function($scope ,  WMService ,  LotService ,  LotViewState ,  AuctionService ,  Auction ,  AddressService ,  FilterService ,  $location ,  $http ,  $filter ,  $timeout, $rootScope) {
	$scope.location = $location;
	$scope.WMService = WMService;
	$scope.AuctionService = AuctionService;
	$scope.Auction = Auction;
	$scope.AddressService = AddressService;
	$scope.LotService = LotService;
	$scope.LotViewState = LotViewState;
	$scope.FilterService = FilterService;
	$scope.lots = {};
	$scope.lotsType = viewVars.lotsType;
	$scope.auction = null;
	// Store auction registrations here and link each lot.auction.auction_registration to an element in this object. Then, whenever we update a lot that
	// results in an updated auction registration, we can simply update the auction_registration in this list with new data (such as an updated
	// total_applied_deposits). Then all lots that belong to the same auction will also have the correct auction_registration with total_applied_deposits.
	//
	// This synchronization is especially very important to do in the auction lot list page because the deposits toolbar at the top needs to be updated
	// whenever any lot is updated. This updates the total_applied_deposits amount. See $scope.syncAuctionRegistrations() to see where it is called.
	// And make sure to call it whenever we refresh a list of lots otherwise we will end up with bugs where the authorized deposit won't update.
	$scope.auctionRegistrations = {};
	$scope.ajaxLotListParams = viewVars.ajaxLotListParams;
	$scope.groups = {};
	$scope.reconnectAttempts = 0;
    $scope.heartbeatLengthError = false;
        if (typeof $scope.model === 'undefined') {
        $scope.model = {
            heartbeatPromise: null, // Used by heartbeat() to store the heartbeat timeout, which throws heartAttack() if necessary.
        }
    }

	var queryParams = FilterService.queryParams();

	$scope.allLots = [];

	//this is the number of lots to load when the lazy loader reaches a specific area as defined in findCurrentLotInView.
	//this is also the initial number of lots to show. Grid needs to show more but since it is less information it SHOULD be ok
	var lazyLoadOffset = 10;
	if(FilterService.filters.current.view == 'grid'){
		lazyLoadOffset = 30;
	}
    if (viewVars.brand === 'sagafurs') {
        lazyLoadOffset = 100;
    }

	$scope.lotHeight = 0;
	$scope.firstLotTop = 0;
	$scope.currentInViewLot = 0;
	$scope.lotOffsets = [];

	$scope.isWebsocketAvailable = viewVars.hasOwnProperty('websocket') && viewVars.websocket && viewVars.websocket.url != null && LotService.isWebsocketProtocolCorrect() === true;

	$scope.lotsRefreshTimeout = null;
	// Secondary refresh: Let's allow up to one refresh within the usual 30 sec timer so that
	// up to one lot can refresh itself when it hits 0 secs. This parameter is used by timers
	// when they hit 0 secs.
	$scope.secondaryLotsRefreshAvailable = true;
	$scope.lotsRefreshFn = function(refreshType){
		var listLots;
		if (viewVars.isLotsMapView){
			listLots = $scope.listLots;
		}
		else {
			listLots = $scope.lots;
		}

		var isSecondaryRefresh = false;
		var isWebsocketAuctionEndRefresh = false;
		if (typeof refreshType != 'undefined'){
			// We are defining refreshType == true to mean a secondary refresh for backward compatibility with angular timers in html.
			isSecondaryRefresh = refreshType == 'secondary' || refreshType == true;
			isWebsocketAuctionEndRefresh = refreshType == 'websocketAuctionEnd';
		}

		var websocketAvailable = $scope.isWebsocketAvailable;

		var refreshAvailable = false;
		if (!isSecondaryRefresh && !isWebsocketAuctionEndRefresh){
			refreshAvailable = !websocketAvailable && $scope.AuctionService.isRefreshable($scope.auction, listLots);
		}
		else if (isSecondaryRefresh){
			refreshAvailable = !websocketAvailable && $scope.secondaryLotsRefreshAvailable && $scope.AuctionService.isRefreshable($scope.auction, listLots);
		}
		else if (isWebsocketAuctionEndRefresh){
			refreshAvailable = true;
		}

		if (refreshAvailable){
			var hasLazyLoader = viewVars.features.lotListV2 && !viewVars.isLotsMapView;
			//todo we need to find a better way to handle this preserved data.
			//perhaps we make a preserve data variable that stores them by the row_id thus allowing us to go quicker through the items.
			var promise = $http.get(viewVars.endpoints.lotsAjax + '?' + $.param($scope.ajaxLotListParams));
			promise.success(function(response){
				
				var preserveData = {};
				if(hasLazyLoader){
					//if we have lotListV2 we are using the lazy loader so get the preserveData from there. We will have to check that scope.lots[i] is defined however
					var preserveData = {};
					for (var i = $scope.allLots.result_page.length - 1; i >= 0; i--) {
						var rowId = $scope.allLots.result_page[i].row_id;
						preserveData[rowId] = {web_module: null};
						if ($scope.allLots.result_page[i].hasOwnProperty("web_module")){
							preserveData[rowId].web_module = $scope.allLots.result_page[i].web_module;
						}
						for (var key in $scope.allLots.result_page[i]){
							if (key.startsWith('_')){
								preserveData[rowId][key] = $scope.allLots.result_page[i][key];
							}
						}
					};
				}else{
					for (var i = listLots.result_page.length - 1; i >= 0; i--) {
						var rowId = listLots.result_page[i].row_id;
						preserveData[rowId] = {web_module: null};
						if (listLots.result_page[i].hasOwnProperty("web_module")){
							preserveData[rowId].web_module = listLots.result_page[i].web_module;
						}
						for (var key in listLots.result_page[i]){
							if (key.startsWith('_')){
								preserveData[rowId][key] = listLots.result_page[i][key];
							}
						}
					};
				}

				//listLots = response;
				//new lots appended. existing lots refreshed.
				var newLots = [];
				var newAllLots = [];
				//console.log(response);
				for(var i = 0; i<response.result_page.length; i++){
					
					var isMatched = false;
					for(var j=0; j<listLots.result_page.length; j++){
						if(listLots.result_page[j].row_id == response.result_page[i].row_id){
							//we found the match so set it
							listLots.result_page[j] = response.result_page[i];
							isMatched = true;
							break;
						}
					}
					if(!isMatched){
						newLots.push(response.result_page[i]);
					}
					//unfortunately we have to do both lots and allLots. fortunately we only have to do it for lotListV2
					if(hasLazyLoader){
						var isMatchedAll = false;
						for(var j=0; j<$scope.allLots.result_page.length; j++){
							if($scope.allLots.result_page[j].row_id == response.result_page[i].row_id){
								//we found the match so set it
								$scope.allLots.result_page[j] = response.result_page[i];
								isMatchedAll = true;
								break;
							}
						}
						if(!isMatchedAll){
							newAllLots.push(response.result_page[i]);
						}
					}
				}
				if(newLots.length>0){
					//add the new lots to the end
					listLots.result_page = listLots.result_page.concat(newLots);
				}
				if(newAllLots.length>0){
					//add the new lots to the end
					$scope.allLots.result_page = $scope.allLots.result_page.concat(newAllLots);
				}

				listLots.result_page = WMService.afterLots(listLots.result_page);
				$scope.syncAuctionRegistrations(listLots);
				if(viewVars.features.lotListV2){
					$scope.allLots.result_page = WMService.afterLots($scope.allLots.result_page);
					$scope.syncAuctionRegistrations($scope.allLots);
				}

            	for (var i=0; i<listLots.result_page.length; i++){
            		if (typeof listLots.result_page[i] != 'undefined'){
                		var rowId = listLots.result_page[i].row_id;
                		if (rowId in preserveData){
                    		$.extend(listLots.result_page[i], preserveData[rowId]);
                		}
                	}
            	}
                if(hasLazyLoader){
            		for (var i=0; i<$scope.allLots.result_page.length; i++){
                		if (typeof $scope.allLots.result_page[i] != 'undefined'){
                    		var rowId = $scope.allLots.result_page[i].row_id;
                    		if (rowId in preserveData){
                    			$.extend($scope.allLots.result_page[i], preserveData[rowId]);
                    		}
                    	}
                	}
                }

                $scope.$broadcast('timer-start'); //this is how we update the timer!!!!
			});
			promise.error(WMService.handleError);
		}

		//stop apply from happening if digest is already in progress
		if(!$scope.$$phase){	
			$scope.$apply();
		}
		if (!isSecondaryRefresh){
			$scope.lotsRefreshWrapper();	
		}
		else {
			// Within the usual 30 sec refresh timer, we won't allow another
			// secondary refresh.
			$scope.secondaryLotsRefreshAvailable = false;
		}
	};
	// Aliasing the function so that we can use a mobile bid popup on both list and detail pages
	// without having to account for two different functions.
	$scope.lotRefreshFn = $scope.lotsRefreshFn;
	$scope.lotsRefreshWrapper = function(){
		if (!$scope.isWebsocketAvailable){
            if ($scope.reconnectAttempts >= viewVars.timedWebSocketMaxRetries) {
                console.log('fall back to timed refresh', $scope.reconnectAttempts);
            }
			if ($scope.lotsRefreshTimeout){
				$timeout.cancel($scope.lotsRefreshTimeout);
			}
			$scope.lotsRefreshTimeout = $timeout($scope.lotsRefreshFn, viewVars.lotsRefreshTimer);
			// Allow a secondary refresh since we have a new 30 second window.
			$scope.secondaryLotsRefreshAvailable = true;
		}
	}

	$scope.registerWebSocket = function(){
		if (viewVars.isLotsMapView){
			return $scope.$parent.registerWebSocket($scope.connection);
		}
		var connectMessage;
		$scope.model.connected = true;
		connectMessage = LotService.webSocketConnectMessage();

		console.log(connectMessage);
		$scope.connection.send(JSON.stringify(connectMessage));		
	}

	$scope.initWebSocket = function(){
		return LotService.webSocketInit($scope);
	}

	$scope.heartbeat = function(){
		// capture the time of the heartbeat and store it in localStorage.
        // compare that to the current time, if it is greater than x show the disconnect message
        var actualTime = new Date().getTime();
        var heartbeatTime = window.localStorage.getItem('heartbeatTime');
        var actualTimeMoment = moment(actualTime);
        var heartbeatTimeMoment = moment(parseInt(heartbeatTime));
        var duration = moment.duration(actualTimeMoment.diff(heartbeatTimeMoment));
        var diffInSeconds = duration.asSeconds();

        if (diffInSeconds > 10 || diffInSeconds < -10) {
            if ($scope.heartbeatLengthError === false) {
                window.scrollTo(0, 0);
            }
            $scope.heartbeatLengthError = true;
        }

        if ($scope.model.heartbeatPromise){
            var actualTime = new Date().getTime();
            window.localStorage.setItem('heartbeatTime', actualTime);
            $timeout.cancel($scope.model.heartbeatPromise);
        }
        $scope.model.heartbeatPromise = $timeout($scope.heartAttack, 6000);
    };

    $scope.heartAttack = function(){
        $scope.connection.close();
        $scope.initWebSocket();
    };

	$scope.registerWebSocket = function(){
		var connectMessage;
		$scope.model.connected = true;
		connectMessage = LotService.webSocketConnectMessage();

		console.log(connectMessage);
		$scope.connection.send(JSON.stringify(connectMessage));		
	}

	$scope.executeMessage = function(message){
		return LotService.webSocketExecuteMessage($scope, message, $scope.lots.result_page);
	}

	if ($scope.isWebsocketAvailable && !viewVars.isLotsMapView){
		$scope.initWebSocket();
	}
	if (typeof $scope.model == 'undefined' || $scope.model == null){
		$scope.model = {};
	}
	$scope.model['auctionInfoVisible'] = false;

	$scope.auctionDetailsStyle = {'max-height':0};
    $scope.auctionDetailsPremiumStyle = { 'max-height': 170 };
	if (viewVars.features.auctionDetailsOpenOnLotList){
		$scope.model.auctionInfoVisible = true;
		$scope.auctionDetailsStyle = {};
	}

	$scope.simpleLotList = function(lots, startPos){
		var simpleLotList = [];
		for(var i = startPos; i<lots.length; i++){
			if (lots[i].hasOwnProperty('auction') && lots[i].auction !== null) {
				simpleLotList.push({row_id: lots[i].row_id, lot_number: lots[i].lot_number, lot_number_extension: lots[i].lot_number_extension, auction: {row_id: lots[i].auction.row_id}, "_placeholder": true});
			}
		}
		return simpleLotList;
	}

	$scope.init = function(lots, auction){
        //this is the number of lots to load when the lazy loader reaches a specific area as defined in findCurrentLotInView.
        //this is also the initial number of lots to show. Grid needs to show more but since it is less information it SHOULD be ok
        var lazyLoadOffset = 10;
        if(FilterService.filters.current.view == 'grid'){
            lazyLoadOffset = 30;
        }
		lots.result_page = WMService.afterLots(lots.result_page);
        window.localStorage.removeItem('heartbeatTime');


		/*
        * Lazy load for loots (disalbe) AM-37780
        *
        if(viewVars.features.lotListV2){
            $scope.allLots = lots;
            $scope.lots.query_info = $scope.allLots.query_info;
            $scope.lots.result_page = $scope.allLots.result_page.slice(0, lazyLoadOffset);
            var simpleLotList = $scope.simpleLotList($scope.allLots.result_page, lazyLoadOffset);

            if(!viewVars.features.nonStardardLotListSizes){
                $scope.lots.result_page = $scope.lots.result_page.concat(simpleLotList);
            }

            $scope.lots = lots;
        }else{
            $scope.lots = lots;
        }
        */
		$scope.lots = lots;

		if(typeof(auction) != 'undefined' && auction != null)
			$scope.auction = AuctionService.afterAuction(auction);
		
		$scope.FilterService.init($scope.lots.query_info);
		
		$scope.paginationPageNumbers = Array.range($scope.FilterService.filters.current.page-2,$scope.FilterService.filters.current.page+2);
		$scope.lotsRefreshWrapper();
		$scope.syncAuctionRegistrations($scope.lots);
		//console.log($scope.FilterService.filters.current);
		//console.log($anchorScroll.yOffset);
	};

	$scope.loadMoreLots = function(){
		if(!viewVars.features.nonStardardLotListSizes){
			loadSpecificLots($scope.currentInViewLot);
		}else{
			$scope.lots.result_page = $scope.lots.result_page.concat($scope.allLots.result_page.slice($scope.lots.result_page.length, lazyLoadOffset+$scope.lots.result_page.length))
		}
	}

	function loadSpecificLots(currentInViewLot){
		var startOffset = currentInViewLot - lazyLoadOffset;
		if(startOffset < 0){
			startOffset = 0;
		}
		var endOffset = currentInViewLot + lazyLoadOffset;
		if(endOffset > $scope.lots.result_page.length-1){
			endOffset = $scope.lots.result_page.length-1;
		}
		//console.log(startOffset, endOffset)
		for(var i = startOffset; i<=endOffset; i++){
			if(!$scope.lots.result_page[i].hasOwnProperty('title')){
				$scope.lots.result_page[i] = $scope.allLots.result_page[i];
			}
		}
		//really do not like to do this but no other way to refresh it otherwise
		if(!$scope.$$phase){
			$scope.$apply();
		}
	}

	$scope.toggleAuctionInfo = function(){
		$scope.model.auctionInfoVisible = !$scope.model.auctionInfoVisible;
		if (viewVars.brand != 'alexcooper'){
			if ($scope.model.auctionInfoVisible){
				var $auctionDetails = $(".auction-details, ."+viewVars.brand+"-auction-details");
				if ($auctionDetails.length){
					$scope.auctionDetailsStyle['max-height']	= $auctionDetails.height() + 1;
				}
			}
			else {
				$scope.auctionDetailsStyle['max-height'] = 0;
			}
		}
	};

    $(function () {
        if ($scope.isOverflown('.auction-info-wrapper') === true) {
            $scope.model.auctionInfoExpanded = false;
            $scope.model.auctionInfoCanExpand = true;
        } else {
            $scope.model.auctionInfoExpanded = true;
            $scope.model.auctionInfoCanExpand = false;
        }
    });
    $scope.toggleAuctionInfoPremium = function(){
        $scope.model.auctionInfoExpanded = !$scope.model.auctionInfoExpanded;
        var $auctionInfoWrapper = $(".auction-info-wrapper");
        if ($scope.model.auctionInfoExpanded){
            $scope.auctionDetailsPremiumStyle['max-height'] = $auctionInfoWrapper[0].scrollHeight + 30;
        } else {
            $scope.auctionDetailsPremiumStyle['max-height'] = 170;
        }
        if(!$scope.$$phase){
            $scope.$apply();
        }
    };

	$scope.subtitle = function(){
		var numLots = $scope.lots.query_info.total_num_results;
		if ($scope.hasOwnProperty('auction') && $scope.auction){
			return WMService.auctionSubtitle($scope.auction);
		}
		return null;
		var fullSubtitle = numLots + ' Lot';
		var separator = " • ";
		if (numLots != 1){
			fullSubtitle += 's';
		}
		return fullSubtitle;
	};
	
	$scope.title = function(){
		return viewVars.title;
	}

	$scope.breadcrumb = function(index){
		if ($scope.auction){
			if (1 == index){
				var auctionIsPast = WMService.auctionIsPast($scope.auction);
				var breadcrumbItem = {title: 'Auctions'};
				if (auctionIsPast){
					breadcrumbItem.title = 'Past '+breadcrumbItem.title;
					breadcrumbItem.url = $scope.WMService.endpoints.pastAuctions;
				}
				else {
					breadcrumbItem.title = 'Upcoming '+breadcrumbItem.title;
					breadcrumbItem.url = $scope.WMService.endpoints.upcomingAuctions;
				}
				return breadcrumbItem;
			}
			else if (2 == index){
				return {title: $scope.auction.title, url: window.location.pathname};
			}
		}
		else {
			if ($scope.lotsType == 'artist'){
				if (1 == index){
					return {title: 'Favorite '+(viewVars.artistLabel.charAt(0).toUpperCase() + viewVars.artistLabel.slice(1))+'s', url: viewVars.endpoints.favoriteArtists};
				}
				else if (2 == index){
					return {title: $scope.title(), url: window.location.href};
				}
			}
			else if (1 == index) {
				return {title: $scope.auction.title, url: window.location.href};
			}
		}
	};

	$scope.firstAuctionLot = function(parent, lots){
		for(var i=0; i<lots.length; i++){
			if(lots[i].auction && lots[i].auction.row_id == parent){
				return lots[i].row_id;
			}
		}
	}
	$scope.countLotsInParentGroup = function(parent, lots){
		if(viewVars.features.smartFilters && viewVars.currentRouteName=='auction-lots-index'){
			//because we have smart filters we need to return some different results
			return FilterService.queryInfo.total_num_results;
		}
		var ct = 0;
		for(var i=0; i<lots.length; i++){
			if(lots[i].auction && lots[i].auction.row_id == parent){
				ct++;
			}
		}
		return ct;
	}

	$scope.lotGroup = function(lot){
		var currBid = null;
		var currGroupKey = null;
		var currGroupLabel = null;
		var groupDetail = null;
		var quantity;
		var temp_quantity;
		var submittable;
		var deletable;
		var quantityable;

		currBid = LotService.currentBid(lot);
		// If there's no bid for this lot anymore, it means it was deleted, remove it from view.
		if (!currBid){
			return null;
		}
		// Determine the group id for current lot, and add to groupIds to keep track of what groups we've discovered so far.
		if (!currBid.hasOwnProperty('group_id') || currBid.group_id == null){
			if (currBid.type == 'live'){
				currGroupKey = "liveBid";
			}
			else {
				currGroupKey = "singleBid";	
			}
		}
		else {
			currGroupKey = currBid.group_id;
		}

		if($scope.groups[currGroupKey]){
			return $scope.groups[currGroupKey];
		}

		if (currGroupKey == "singleBid" || currGroupKey == "liveBid"){
			if (currGroupKey == "singleBid"){
				if (viewVars.features.groupBidding){
					currGroupLabel = "Single Bids";
				}
				else {
					currGroupLabel = "Absentee Bids";
				}
			}
			else {
				currGroupLabel = "Live Bids";
			}
			submittable = false;
			deletable = false;
			quantityable = false;
			temp_quantity = null;
			quantity = null;
			order_field = '';
		}
		else {
			currGroupLabel = LotService.groupIdToLabel(currBid.group_id);
			submittable = true;
			deletable = true;
			quantityable = true;
			var groupDetails = LotService.groupDetails(lot.auction.row_id, currBid.group_id);
			if (groupDetails){
				temp_quantity = groupDetails.max_quantity; // Used to store the quantity as represented by the select input field
				quantity = groupDetails.max_quantity; // Used to store the actual quantity as represented by the server
			}
			// If for whatever reason, the group is not actually defined on the server (in the auction_registrations.either_or.groups object), just
			// set some default values instead of breaking the page.
			else {
				temp_quantity = 1;
				quantity = 1;
			}
			order_field = currBid.group_id;
		}
		var group = {
			submittable: submittable,
			deletable: deletable,
			quantityable: quantityable,
			label: currGroupLabel,
			group_id: currBid.group_id,
			temp_quantity: temp_quantity,
			quantity: quantity,
			lots: [],
			order_field: order_field
		};
		// If this bid is marked as pending, add a submit button for the group.
		if (currBid.type == 'absentee' && !currBid.confirmed){
			group.submittable = true;
		}

		$scope.groups[currGroupKey] = group;

		return group;
	};

	$scope.numLotsInGroup = function(lots,group){
		var numLots = 0;
		for (var i = 0; i < lots.result_page.length; i++) {
			if ($scope.lotGroup(lots.result_page[i]) && $scope.lotGroup(lots.result_page[i]).group_id == group.group_id){
				numLots = numLots + 1;
			}
		};
		return numLots;
	}
	$scope.isFirstLotInGroup = function(lot,lots,group){
		for (var i = 0; i < lots.result_page.length; i++) {
			if ($scope.lotGroup(lots.result_page[i]) && $scope.lotGroup(lots.result_page[i]).group_id == group.group_id){
				return lot.row_id == lots.result_page[i].row_id;
			}
		};
		return false;
	}
	/* Return true iff the previous lot is part of a different auction than the given lot. */
	$scope.isLotInNewAuctionLocally = function(lot,lots){
		var previousAuctionId = null;
		for (var i = 0; i < lots.result_page.length; i++) {
			if (!lots.result_page[i].auction){
				continue;
			}
			// Found the lot, return true only if the previous lot is null or has a different auction id
			if (lots.result_page[i].row_id == lot.row_id){
				return !previousAuctionId || lot.auction.row_id != previousAuctionId;
			}
			previousAuctionId = lots.result_page[i].auction.row_id;
		};
		return false;
	}
	/* Return true iff the previous lot is part of a different auction date than the given lot. */
	$scope.isLotInNewDateLocally = function(lot,lots){
		var previousAuctionDate = null;
		for (var i = 0; i < lots.result_page.length; i++) {
			if (!lots.result_page[i].auction){
				continue;
			}
			// Found the lot, return true only if the previous lot is null or has a different auction id
			if (lots.result_page[i].row_id == lot.row_id){
				return !previousAuctionDate || moment(lot.auction.time_start).startOf('day').format() != previousAuctionDate;
			}
			previousAuctionDate = moment(lots.result_page[i].auction.time_start).startOf('day').format();
		};
		return false;
	}
	/* Return true iff the previous lot is part of a different county than the given lot. */
	$scope.isLotInNewCountyLocally = function(lot,lots){
		var previousAuctionCounty = null;
		for (var i = 0; i < lots.result_page.length; i++) {
			if (!lots.result_page[i].auction){
				continue;
			}
			// Found the lot, return true only if the previous lot is null or has a different auction county
			if (lots.result_page[i].row_id == lot.row_id){
				return !previousAuctionCounty || lot.auction.county != previousAuctionCounty;
			}
			previousAuctionCounty = lots.result_page[i].auction.county;
		};
		return false;
	}
	/* Return true iff the next lot is null or is part of a different auction. */
	$scope.isLastLotInAuctionLocally = function(lot, lots){
		for (var i = 0; i < lots.result_page.length; i++) {
			// Found the lot, return true only if the next lot is null or has a different auction id
			if (lots.result_page[i].row_id == lot.row_id){
				return i+1 == lots.result_page.length || (!lots.result_page[i+1].auction || lots.result_page[i+1].auction.row_id != lot.auction.row_id);
			}
		};
		return false;
	}
	/** 
	 *  Determines whether the given lot is the first lot in the list with lot.auction.time_start.
	 *  Note that we are not taking into account any timezone differences, so we just assume local browser timezone which is most likely EST for AlexCooper.
	 */ 
	$scope.isFirstLotInDateLocally = function(lot,lots){
		var date = null;
		if (lot.auction && lot.auction.time_start){
			date = moment(lot.auction.time_start).startOf('day').format();
		}
		var datesDiscovered = [];
		for (var i = 0; i < lots.result_page.length; i++) {
			if (!lots.result_page[i].auction || !lots.result_page[i].auction.time_start){
				continue;
			}
			if (lots.result_page[i].row_id == lot.row_id){
				return datesDiscovered.indexOf(date) == -1;
			}
			var startOfDate = moment(lots.result_page[i].auction.time_start).startOf('day').format();
			if (datesDiscovered.indexOf(startOfDate) == -1){
				datesDiscovered.push(startOfDate);
			}
		};
		return false;
	}
	$scope.isForeclosure = function(lot){
		return LotService.lotType(lot) == 'foreclosure';
	}

	$scope.setBidStatus = function(status){
		location.search = $.param({bid_status: status});
	};
	$scope.setAbsenteeBidStatus = function(status){
		location.search = $.param({absentee_bid_status: status});
	};
	$scope.paginationPageUrl = function(page){
		var filters = $.extend({}, FilterService.filters.current);
		filters.page = page;
		for (var key in filters){
			if (filters[key] == null){
				delete filters[key];
			}
		}
		return $.param(filters);
	};
	//$scope.focus = function(lotId){console.log($("[name=max_bid][data-lot-id='"+lotId+"']"));};
	/*$scope.viewCategory = function(categoryId){
		alert($scope.lots.result_page);
		if (true){
			$scope.setFilter('category', categoryId, true);
		}
	};*/
	$scope.setLotsType = function(newLotsType){
		if (newLotsType == 'auction'){
			window.location.href = viewVars.endpoints.auctionLots + $scope.auction.row_id;
		}
		else if (newLotsType == 'bids'){
			window.location.href = viewVars.endpoints.bidSheet + $scope.auction.row_id;
		}
	}

	$scope.syncAuctionRegistrations = function(lots){
		for (var i=0; i<lots.result_page.length; i++){
			if (lots.result_page[i].auction){
				if ($scope.auctionRegistrations.hasOwnProperty(lots.result_page[i].auction.row_id) && $scope.auctionRegistrations[lots.result_page[i].auction.row_id]){
					lots.result_page[i].auction.auction_registration = $scope.auctionRegistrations[lots.result_page[i].auction.row_id];
				}
				else {
					$scope.auctionRegistrations[lots.result_page[i].auction.row_id] = lots.result_page[i].auction.auction_registration;
				}
			}
		}
	}

	function findCurrentLotInView(num, arr) {
		var mid;
		var lo = 0;
		var hi = arr.length - 1;
		while (hi - lo > 1) {
			mid = Math.floor ((lo + hi) / 2);
			if (arr[mid] < num) {
				lo = mid;
			} else {
				hi = mid;
			}
		}
		if (num - arr[lo] <= arr[hi] - num) {
			return lo;
			//return arr[lo];
		}
		//return arr[hi];
		return hi;
	}

		/**
		 * Lazy load (disable) AM-37780
		 *
	$(window).scroll(function(){
		//calculate top and height of first lot. 
		//we only use the lazy loader for lot list v2 so we need to lock this out
		if(viewVars.features.lotListV2 && $scope.lots.result_page.length > 1){
			var windowScroll = $(window).scrollTop();
			if($scope.lotHeight == 0){
				$scope.lotHeight = $('.lot-repeater').first().outerHeight();
			}
			if($scope.firstLotTop == 0){
				$scope.firstLotTop = $('.lot-repeater').first().position().top;
			}
			
			//$scope.currentInViewLot = Math.floor(windowScroll / $scope.lotHeight) -1;
			//if($scope.currentInViewLot < 0){
			//	$scope.currentInViewLot = 0;
			//}
			$scope.currentInViewLot = findCurrentLotInView(windowScroll, $scope.lotOffsets);
			var firstLotToLoad = $scope.currentInViewLot - lazyLoadOffset; 
			if(firstLotToLoad < 0){
				firstLotToLoad = 0;
			}
			var lastLotToLoad = $scope.currentInViewLot + lazyLoadOffset;

			if(lastLotToLoad > $scope.allLots.result_page.length){
				lastLotToLoad = $scope.allLots.result_page.length;
			}

			//console.log("in view ", $scope.currentInViewLot, $scope.lots.result_page[lastLotToLoad-2].hasOwnProperty('title'), lastLotToLoad);
			if((typeof $scope.lots.result_page[lastLotToLoad-2] != 'undefined' && !$scope.lots.result_page[lastLotToLoad-2].hasOwnProperty('title')) || (typeof $scope.lots.result_page[firstLotToLoad] != 'undefined' && !$scope.lots.result_page[firstLotToLoad].hasOwnProperty('title'))){
				$scope.loadMoreLots();
			}
		}
	});

	*/
	

	$(function(){
		$('.lot-repeater').each(function(){
			$scope.lotOffsets.push($(this).position().top);
		});
	});

	$scope.$watch('FilterService.filters.current.view', function(val){
		if(val == 'grid'){
			lazyLoadOffset = 30
		}else{
			lazyLoadOffset = 10;
		}
		$scope.lotOffsets = [];
		$scope.$$postDigest(function() {
			//execute after the digest cycle so that we can be sure the view has changed to allow us to get the positions
			$('.lot-repeater').each(function(){
				$scope.lotOffsets.push($(this).position().top);
			});
		});
        if (val == 'list' && viewVars.features.enlargeThumbnailImagesPopup && ['auction-lots-index-slug', 'lots-index'].indexOf(viewVars.currentRouteName) !== -1) {
            $rootScope.popoverThumbnailLots(500);
        }
	});
	
	if (viewVars.hasOwnProperty('lots') && viewVars.lots){
		$scope.init(viewVars.lots, viewVars.auction);
	}

	$scope.showMobileFilters = function(){
		$('.mobile-filters-screen').animate({
			right: "0%"
		});
	}

    $scope.submitBids = function(){
        var submittedBids = [];
        var lots = $scope.lots.result_page;
        $scope.bulk_data = [];
        $scope.bulkLots = [];
        $scope.bidLotData = [];
        for(i in lots){
            if(lots[i].web_module.hasOwnProperty('bulkBid') && lots[i].web_module.bulkBid == true){
                if(lots[i].web_module.absentee_bid.hasOwnProperty("amount") && lots[i].web_module.absentee_bid.amount){
                    $scope.bulk_data.push({'lot_id':(lots[i].absentee_bid && lots[i].absentee_bid.lot_id) ? lots[i].absentee_bid.lot_id : lots[i].row_id});
                    $scope.bulkLots.push(lots[i]);
                }
            }
        }
        for(var i=0; i<$scope.bulk_data.length; i++){
            if($scope.bulk_data[i].hasOwnProperty('lot_id')){
                var lot = $scope.bulkLots[i];
                var tmp = {
                    lot_id: $scope.bulk_data[i].lot_id,
                    confirmed: true,
                };
                if(WMService.isPercentageBiddingEnabled(lot)){
                    tmp.max_bid_percentage = lot.web_module.absentee_bid.amount;
                }else{
                    tmp.max_bid = lot.web_module.absentee_bid.amount;
                }

                submittedBids.push(tmp);
                $scope.bidLotData.push(lot);
            }
        }
        var promise = $http.post(WMService.generateUrl('ajaxQuickBid', {'auctionId': viewVars.auction.row_id}), submittedBids);
        promise.success(function(data){
            lot.web_module.updateInProgress = false;
            for(var i=0; i<$scope.bidLotData.length; i++){
                if (!data.result_page[i]._outbid_absentee_bid && (data.hasOwnProperty('me') === true || viewVars.features.bidsInLotObject === true)) {
                    LotService.exitAbsenteeBidEditMode($scope.bidLotData[i]);
                    var newBidAmount = BigNumber($scope.bidLotData[i].web_module.absentee_bid.amount).toFixed(2);
                    if(data.result_page[i].absentee_bid.max_bid){
                        var oldBidFormatted = LotService.formatBidAmount(data.result_page[i].absentee_bid.max_bid);
                    } else {
                        oldBidFormatted = LotService.formatBidAmount(data.result_page[i].absentee_bid.max_bid_percentage);
                    }
                    if (oldBidFormatted !== newBidAmount && viewVars.currentRouteName !== 'live-auction') {
                        $scope.bidLotData[i].web_module.absentee_bid.rounded_amount_message_open = true;
                        var popupDuration = 5000;
                        $timeout(function(){
                            for(var j=0; j<$scope.bidLotData.length; j++){
                                $scope.bidLotData[j].web_module.absentee_bid.rounded_amount_message_open = false;
                            }
                        },popupDuration);
                        $scope.bidLotData[i].web_module.absentee_bid.rounded_amount_message_title = $filter('translate')("Bid Rounded Down to Nearest Bid Increment");
                        $scope.bidLotData[i].web_module.absentee_bid.rounded_amount_message_content = $filter('translate')("Feel free to increase your absentee bid to the next increment.");
                    } else {
                        $scope.bidLotData[i].web_module.absentee_bid.rounded_amount_message_title = "";
                        $scope.bidLotData[i].web_module.absentee_bid.rounded_amount_message_content = "";
                    }
                    $scope.bidLotData[i]._bidMode = 'view';
                    $scope.bidLotData[i].web_module.absenteeBidEditMode = false;
                    $scope.bidLotData[i].web_module.previousAbsenteeBidEditMode = false;
                }
            }
            var fieldsetType = 'detail';
            angular.forEach(data.result_page, function(response) {
                var lotPromise = $http({method: 'GET', url: viewVars.endpoints.lotAjax+response.auction_lot_id + '/' + fieldsetType});
                var preservedAuctionReg = null;
                if (response.auction && response.auction.auction_registration){
                    preservedAuctionReg = response.auction.auction_registration;
                }
                lotPromise.success(function(lotData){
                    if (preservedAuctionReg){
                        $.extend(true, preservedAuctionReg, lotData.response.auction.auction_registration);
                        lotData.response.auction.auction_registration = preservedAuctionReg;
                    }
                    for(var i=0; i < $scope.bidLotData.length; i++){
                        if($scope.bidLotData[i].lot_number === lotData.response.lot_number){
                            lot = $scope.bidLotData[i];
                        }
                    }
                    $.extend(lot,lotData.response);
                    LotService.recalculateBulkBids(lot);
                    $rootScope.bulkBidCount = 0;
                    $rootScope.bulkBidArray = [];
                });
                lotPromise.error(function(error){
                });
            });
        });
        promise.error(function(error){
            WMService.handleLotErrorFn(lot)(error);
            lot.web_module.updateInProgress = false;
        });
    }
    $scope.WMService.calculateLocalTimeDifferenceWithServerTime();
}]);
