# topology
library for topology information management

Different applications apply different representations of the same market topology. Different market timeframes have different topologies.
This repository includes configurations of some of these topology representations - and mappings between them, where applicable.

A small function library is included for validating topologies according to a few simple rules:
- bidding zones:
--short names should be unique
--EIC codes should be unique
--A bidding zone must have pair-wise in- and out-going borders

- bidding zone borders:
-- name should be unique
-- sending bidding zone should be defined in list of bidding zones
-- receiving bidding zone should be defined in list of bidding zones
-- type must be one of: AC, HVDC, lineset
-- If type is HVDC, then border must be associated with an HVDC definition
-- If type is lineset, then border must be associated with a lineset definition

hej frederik

