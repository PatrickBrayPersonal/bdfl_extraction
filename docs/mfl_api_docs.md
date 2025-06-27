Category             | Endpoint         | Description                                                  | Arguments
---------------------|------------------|--------------------------------------------------------------|------------------------------------------------------------
Common League Info   | league           | General league setup parameters                              | L (League ID, required)
                     | rules            | League scoring rules                                         | L (League ID, required)
                     | rosters          | Current rosters for all franchises                           | L (required), FRANCHISE (optional), W (optional)
                     | freeAgents       | Fantasy free agents for a given league                       | L (required), POSITION (optional)
                     | schedule         | Fantasy schedule for a given league/week                     | L (required), W (optional), F (optional)
                     | calendar         | Summary of league calendar events                            | L (required)
                     | playoffBrackets  | All playoff brackets for a given league                      | L (required)
                     | playoffBracket   | Games of the specified playoff bracket                       | L (required), BRACKET_ID (required)
Transactions         | transactions     | All non-pending transactions for a given league              | L (required), W (optional), TRANS_TYPE (optional)
                     | auctionResults   | Auction results for a given league                           | L (required), DATA (XML string), CLEAR (optional), OVERWRITE (optional)
                     | draftResults     | Draft results for a given league                             | L (required), DATA (XML string)
User Functions       | myleagues        | All leagues of the current user                              | YEAR (optional), FRANCHISE_NAMES (optional)
                     | leagueSearch     | Searches for leagues in the database                         | SEARCH (optional), ID (optional), YEAR (optional)
Fantasy Content      | players          | All player IDs, names, and positions                         | L (optional), DETAILS (optional), SINCE (optional), PLAYERS (optional)
                     | playerProfile    | Summary of information regarding a player                    | P (Player ID or list of IDs, required)
                     | allRules         | All scoring rules supported by MyFantasyLeague.com           | None
                     | playerRanks      | Overall player rankings from FantasySharks.com               | POS (optional), SOURCE (optional)
                     | adp              | Average Draft Position results                               | PERIOD (optional), FCOUNT (optional), IS_PPR (optional)
Draft & Auction      | myDraftList      | Set the players in an owner's My Draft List                  | L (required), FRANCHISE_ID (required), PLAYERS (required)
                     | tradeBait        | Import an owner's trade bait                                 | L (required), WILL_GIVE_UP (required), IN_EXCHANGE_FOR (optional)
Miscellaneous        | ics              | Summary of the league calendar in .ics format                | L (required)


# Example Perl Script
The following Perl script is a sample of how to get the league info for a league a user is in. It shows how to get the cookie from a username and how to identify the host of a league. Set the $league_id, $username and $password variables to appropriate values. Converting this to other languages should be pretty straight-forward as long you have access to an HTTP library.


```
#!/bin/perl

# Set these variables somehow:
my $league_id = "LEAGUE_ID";
my $username = "USERNAME";
my $password = "PASSWORD";
my $year = "2022";

# Defaults
my $proto = "https";
my $api_host = "api.myfantasyleague.com";
my $json = 0;
my $req_type = 'league';

use HTTP::Request::Common qw(GET);  
use LWP::UserAgent; 

$ua = LWP::UserAgent->new();  

my $login_url = "https://$api_host/$year/login?USERNAME=$username&PASSWORD=$password&XML=1";
my $login_req = HTTP::Request->new("GET", $login_url);
print "Making request to get cookie: $login_url\n";
my $login_resp = $ua->request($login_req);
my $cookie;
if($login_resp->as_string() =~ /MFL_USER_ID="([^"]*)">OK/) {
    $cookie = $1;
}
else {
    die "Can not get login cookie.  Response: " .
        $login_resp->as_string() . "\n";
}
print "Got cookie $cookie\n";

my $url = "${proto}://$api_host/$year/export";
my $headers = HTTP::Headers->new("Cookie" => "MFL_USER_ID=$cookie");
my $ml_args = qq(TYPE=myleagues&JSON=$json);
my $ml_req = HTTP::Request->new("GET", "$url?$ml_args", $headers);
print "Making request to get league host: $url?$ml_args\n";
my $ml_resp = $ua->request($ml_req);

# find host in the return string - note that this is for illustrating the
# API. A more robust solution would be to use a proper XML parser.
if($ml_resp->as_string() =~ m!url="(https?)://([a-z0-9]+.myfantasyleague.com)/$year/home/$league_id"!s) {
    $proto = $1;
    my $league_host = $2;
    print "Got league host $league_host\n";
    $url = "${proto}://${league_host}/$year/export";
}
else {
    die "Can't find info for league id $league_id.  Response: " . 
        $ml_resp->as_string() . "\n";
}

my $args = qq(TYPE=$req_type&L=$league_id&JSON=$json);
my $req = HTTP::Request->new("GET", "$url?$args", $headers);
print "Making request to get league info $url?$args\n";
my $resp = $ua->request($req);
print "\nLeague Info:\n";
print $resp->as_string();

print "\n";

``` 	
