
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Predicates for LZV cup tournament
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%This predicate gives whether it is team or not
team(Team):-availability(Team,_,_).

%This predicate gives whether it is slot or not
slot(Slot):-availability(_,Slot,_).

% This predicate gives  whether a team plays in home  or not:
home(Team,Slot):-availability(Team,Slot,1).

% This predicate gives  whether a team plays  away  or not:
away(Team,Slot):-  availability(Team,Slot,0).

% This predicate gives  whether a teams is forbidden to play or not:
forbidden(Team,Slot):-availability(Team,Slot,2).

% R max predicate required for constrain 5
max_R(4).

% M slot predicate required for constrain 6
m_slot(60). 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Code to schedule matches for LZV cup tournament
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% To generate all matches
{match(H, A, S) :  slot(S)}:- team(H), team(A),H!=A .




% Constraint 1 -each team plays a home game against each other team at most once
:- match(H, A1, S1), match(H, A2, S2),S1!=S2,A1=A2.

%Constrain 2 -home team availability Hi (i ∈ T ) is respected
:- match(H, _, S), away(H, S). 
:- match(H, A, S), forbidden(H,S). 

%constrain 3 -  away team unavailability Ai (i ∈ T ) is respected
:- match(H, A, S), forbidden(A,S). 

% Constrain 4 - each team plays at most one game per time slot 
:- match(H1, A, S1), match(H2, A, S2), H1!=H2, S1=S2. % Only one match per slot
:- match(H, A1, S1), match(H, A2, S2), A1!=A2, S1=S2. % Only one match per slot
:- match(H, _, S1), match(_, H, S2), S1=S2.
:- match(_, A, S1), match(A, _, S2), S1=S2.


% Constraint 5 -  each team plays at most 2 games in a period of Rmax time slots 
period(X1, X2) :- slot(X1), slot(X2), X2=X1+R,max_R(R).

home_per_period(X1, X2, T, C) :- C=#count{S: match(T, _, S), period(X1, X2), S>=X1, S<=X2},slot(X1),slot(X2),team(T).

away_per_period(X1, X2, T, C) :- C=#count{S: match(_, T, S), period(X1, X2), S>=X1, S<=X2},slot(X1),slot(X2),team(T).

total_per_period(X1, X2, T, C) :- home_per_period(X1, X2, T, C1), away_per_period(X1, X2, T, C2), C=C1+C2.

:- team(T), slot(S1), slot(S2),total_per_period(S1, S2, T, C),C>2.


%Constrain 6 - there are at least m time slots between two games with the same pair of teams.
:- match(H1, A1, S1), match(A2, H2, S2),A1=A2,H1=H2,S1!=S2,S2>S1,(S2-S1) < M, m_slot(M).
:- match(H1, A1, S1), match(A2, H2, S2),A1=A2,H1=H2,S1!=S2,S1>S2,(S1-S2) < M,m_slot(M).



% To maximize total matches count to get optimal solution
#maximize { 1, match(Home,Away,TS) : match(Home,Away,TS) }.

% Show the successful matches 
#show match/3.


