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
/* CREATE TABLE userAccount() */
/* This table should be provided by another group */

/*==============================================================*/
/* Table: administration                                        */
/*==============================================================*/
DROP TABLE IF EXISTS administration;
CREATE TABLE administration(
    admin           VARCHAR(255)    not null,
    password        VARCHAR(255)    null,
    PRIMARY KEY (admin)
);

/*==============================================================*/
/* Table: flight                                                */
/*==============================================================*/
DROP TABLE IF EXISTS flight;
CREATE TABLE flight(
    flightNumber    VARCHAR(255)    not  null,
    fuelTax         FLOAT           null,
    airportTax      FLOAT           null,
    depatureAirport VARCHAR(255)    null,
    depatureTime    DATETIME        null,
    arrivalAirport  VARCHAR(255)    null,
    arrivalTime     DATETIME        null,
    aircraftType    VARCHAR(255)    null,
    schedule        VARCHAR(255)    null,
    punctuality     FLOAT           null,
    stop            BOOL            null,
    PRIMARY KEY (flightNumber)
);

/*==========================================*/
/* Need a table project AirportNumber to    */
/* their Chinese name and location          */
/*==========================================*/

/* DROP TABLE IF EXISTS flightLocation;     */
/* CREATE TABLE flightLocation(             */
/*     flightNumber    VARCHAR(255)         */
/* )                                        */


/*==============================================================*/
/* Table: hotel                                                 */
/*==============================================================*/
DROP TABLE IF EXISTS hotel;
CREATE TABLE hotel(
    h_id            INT UNSIGNED    AUTO_INCREMENT,
    name            VARCHAR(255)    null,
    description     VARCHAR(255)    null,
    location        VARCHAR(255)    null,
    PRIMARY KEY (h_id)
);

DROP TABLE IF EXISTS room;
CREATE TABLE room(
    h_id            INT UNSIGNED,
    roomType        VARCHAR(255)    not null,
    bedType         VARCHAR(255)    null,
    breakfast       BOOL            null,
    wifi            BOOL            null,
    price           FLOAT           null,
    PRIMARY KEY (h_id, roomType),
    FOREIGN KEY (h_id) REFERENCES hotel(h_id)
);

/*==============================================================*/
/* Table: transaction                                           */
/*==============================================================*/
DROP TABLE IF EXISTS hotelTransaction;
CREATE TABLE hotelTransaction(
    t_id            INT UNSIGNED    AUTO_INCREMENT,
    h_id            INT UNSIGNED    not null,
    u_id            VARCHAR(255)    not null,
    time            DATETIME        null,
    price           FLOAT           null,
    status          VARCHAR(255)    null,
    PRIMARY KEY (t_id),
    FOREIGN KEY (h_id) REFERENCES hotel(h_id)
);

DROP TABLE IF EXISTS flightTransaction;
CREATE TABLE flightTransaction(
    t_id            INT UNSIGNED    AUTO_INCREMENT,
    flightNumber    VARCHAR(255)    not null,
    u_id            VARCHAR(255)    not null,
    time            DATETIME        null,
    price           FLOAT           null,
    status          VARCHAR(255)    null,
    PRIMARY KEY (t_id),
    FOREIGN KEY (flightNumber) REFERENCES flight(flightNumber)
);

/*==============================================================*/
/* Table: comment                                               */
/*==============================================================*/
DROP TABLE IF EXISTS flightComment;
CREATE TABLE flightComment(
    c_id            INT UNSIGNED    AUTO_INCREMENT,
    flightNumber    VARCHAR(255)    not null,
    u_id            VARCHAR(255)    not null,
    message         VARCHAR(500)    null,
    rate            VARCHAR(500)    null,
    PRIMARY KEY (c_id),
    FOREIGN KEY (flightNumber) REFERENCES flight(flightNumber)
);

DROP TABLE IF EXISTS hotelComment;
CREATE TABLE hotelComment(
    c_id            INT UNSIGNED    AUTO_INCREMENT,
    h_id            INT UNSIGNED    not null,
    u_id            VARCHAR(255)    not null,
    message         VARCHAR(500)    null,
    rate            VARCHAR(255)    null,
    PRIMARY KEY (c_id),
    FOREIGN KEY (h_id) REFERENCES hotel(h_id)
);

/*==============================================================*/
/* Table: airport                                               */
/*==============================================================*/
DROP TABLE IF EXISTS airport;
CREATE TABLE airport(
    code            VARCHAR(255)    not null,
    city            VARCHAR(255)    not null,
    name_cn         VARCHAR(255)    not null,
    name_en         VARCHAR(255)    not null,
    domestic        BOOL            not null
);

/*==============================================================*/
/* Table: airlines                                              */
/*==============================================================*/
DROP TABLE IF EXISTS airline;
CREATE TABLE airline(
    code            VARCHAR(255)    not null,
    name_cn         VARCHAR(255)    not null,
    name_en         VARCHAR(255)    not null,
    PRIMARY KEY (code)
);

