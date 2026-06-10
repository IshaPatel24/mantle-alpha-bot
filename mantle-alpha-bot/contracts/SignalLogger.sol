// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title MantleAlpha Signal Logger
/// @notice Permanently logs AI-generated alpha signals on Mantle Network
contract SignalLogger {

    struct Signal {
        uint256 id;
        string signalType;
        string severity;
        uint256 valueUSD;
        uint256 confidence;
        string sourceTxHash;
        address logger;
        uint256 timestamp;
        bool verified;
    }

    uint256 public signalCount;
    mapping(uint256 => Signal) public signals;
    mapping(address => bool) public authorizedLoggers;
    address public owner;

    event SignalLogged(
        uint256 indexed id,
        string signalType,
        string severity,
        uint256 timestamp,
        address indexed logger
    );

    modifier onlyOwner() { require(msg.sender == owner, "Not owner"); _; }
    modifier onlyAuthorized() { require(authorizedLoggers[msg.sender] || msg.sender == owner, "Not authorized"); _; }

    constructor() {
        owner = msg.sender;
        authorizedLoggers[msg.sender] = true;
    }

    function logSignal(
        string calldata signalType,
        string calldata severity,
        uint256 valueUSD,
        uint256 confidence,
        string calldata sourceTxHash
    ) external onlyAuthorized {
        require(confidence <= 100, "Confidence must be 0-100");
        signalCount++;
        signals[signalCount] = Signal({
            id: signalCount,
            signalType: signalType,
            severity: severity,
            valueUSD: valueUSD,
            confidence: confidence,
            sourceTxHash: sourceTxHash,
            logger: msg.sender,
            timestamp: block.timestamp,
            verified: false
        });
        emit SignalLogged(signalCount, signalType, severity, block.timestamp, msg.sender);
    }

    function verifySignal(uint256 signalId) external onlyAuthorized {
        require(signalId > 0 && signalId <= signalCount, "Invalid ID");
        signals[signalId].verified = true;
    }

    function getSignal(uint256 signalId) external view returns (Signal memory) {
        require(signalId > 0 && signalId <= signalCount, "Invalid ID");
        return signals[signalId];
    }

    function getTotalSignals() external view returns (uint256) { return signalCount; }

    function setAuthorizedLogger(address logger, bool status) external onlyOwner {
        authorizedLoggers[logger] = status;
    }
}
