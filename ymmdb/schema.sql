/*==============================================================*/
/* Server Version:      MySQL 5.5.30                            */
/* Created on:     2013-6-3 21:02:14                            */
/*==============================================================*/

/* we don't need to deal with databases since we're using sqlite */
--DROP DATABASE IF EXISTS ymm;
--CREATE DATABASE ymm;
--USE ymm;

/*==============================================================*/
/* Table: userAccount                                           */
/*==============================================================*/
--CREATE TABLE userAccount()

/*==============================================================*/
/* Table: flight                                                */
/*==============================================================*/
CREATE TABLE flight(
    flightNumber    VARCHAR(6)      null,
    fuelTax         FLOAT           null,
    airportTax      FLOAT           null,
    depatureAirport VARCHAR(3)      null,
    depatureTime    DATETIME        null,
    arrivalAirport  VARCHAR(3)      null,
    arrivalTime     DATETIME        null,
    aircraftType    VARCHAR(10)     null,
    schedule        VARCHAR(7)      null,
    punctuality     FLOAT           null,
    stop            BOOL            null
);

/*==============================================================*/
/* Table: hotel                                                 */
/*==============================================================*/
--CREATE TABLE hotel()

/*==============================================================*/
/* Table: comment                                               */
/*==============================================================*/
--CREATE TABLE comment()
