%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Predicates for LZV cup tournament
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This predicate gives  whether a team plays in home  or not:
home(Team,Slot):-availability(Team,Slot,'1').
% This predicate gives  whether a team plays  away  or not:
away(Team,Slot):-  availability(Team,Slot,'0').
% This predicate gives  whether a teams is forbidden to play or not:
forbidden(Team,Slot):-availability(Team,Slot,'2').
%To check home team is not equal toaway team
condition1(Home, Away) :-
    Home \= Away.

%Constrain 2 -home team availability Hi (i ∈ T ) is respected
constarint2(H,S):- home(H,S),not(forbidden(H,S)).

%constrain 3 -  away team unavailability Ai (i ∈ T ) is respected
constarint3(A,S):- not(forbidden(A,S)).

%To generate all match with home and away availability
match(H,A,S):-team(H),team(A),condition1(H, A),slot(S),
constarint2(H,S),
constarint3(A,S).


% Constraint 1 -each team plays a home game against each other team at most once
% Constrain 4 - each team plays at most one game per time slot 
filter_matches([], _, Helper, Helper).
filter_matches([matches(H,A,S)|Tail], Processed, Helper, Filtered) :-
    \+ member(matches(H,A,S), Processed),  
    \+member(matches(H,_,S), Processed),
    \+member(matches(_,A,S), Processed),
    \+member(matches(_,H,S), Processed),
    \+member(matches(A,_,S), Processed),
    \+member(matches(H,A,_), Processed), % This deals with Constraint 1
    filter_matches(Tail, [matches(H,A,S)|Processed], [matches(H,A,S)|Helper], Filtered).
filter_matches([_|Tail], Processed, Helper, Filtered) :-
    filter_matches(Tail, Processed, Helper, Filtered).

%Match generating from Constarint1 and 4
constraint_1_4(Matches, Filtered) :-
    filter_matches(Matches, [], [], Filtered).


%To create list of all matches
constraint_2_3( Schedule) :-
    findall(matches(H,A,S), match(H,A, S), Schedule).
%To generate all matches
all_match(FinalSchedule) :-constraint_2_3(Slots),
constraint_1_4(Slots, FinalSchedule),
    open('Prolog_output.txt', write, Stream),
    write_matches(Stream, FinalSchedule),
    close(Stream).
    
    
write_matches(_, []).
    
write_matches(Stream, [matches(H, A, S) | Rest]) :-
    write(Stream, matches(H, A, S)),
    write(Stream, '.\n'),
    write_matches(Stream, Rest).

