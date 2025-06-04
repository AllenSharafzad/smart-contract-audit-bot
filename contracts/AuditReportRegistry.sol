
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title AuditReportRegistry
 * @dev Smart contract for storing and managing audit reports on-chain
 * @notice This contract demonstrates various security patterns and potential vulnerabilities for testing
 */
contract AuditReportRegistry is Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;
    
    // State variables
    Counters.Counter private _reportIds;
    mapping(uint256 => AuditReport) public auditReports;
    mapping(address => uint256[]) public auditorReports;
    mapping(bytes32 => bool) public contractHashes;
    
    // Events
    event ReportSubmitted(
        uint256 indexed reportId,
        address indexed auditor,
        bytes32 indexed contractHash,
        uint8 severity,
        uint256 timestamp
    );
    
    event ReportUpdated(
        uint256 indexed reportId,
        address indexed auditor,
        uint256 timestamp
    );
    
    event AuditorRegistered(address indexed auditor, uint256 timestamp);
    
    // Structs
    struct AuditReport {
        uint256 id;
        address auditor;
        bytes32 contractHash;
        string contractName;
        string ipfsHash;
        uint8 severity; // 1-5 scale
        uint256 timestamp;
        bool isActive;
        uint256 fee;
    }
    
    struct Auditor {
        bool isRegistered;
        uint256 reputation;
        uint256 totalReports;
        uint256 registrationTime;
    }
    
    // Mappings
    mapping(address => Auditor) public auditors;
    mapping(uint256 => string[]) public reportTags;
    
    // Constants
    uint256 public constant REGISTRATION_FEE = 0.1 ether;
    uint256 public constant REPORT_FEE = 0.01 ether;
    uint256 public constant MAX_SEVERITY = 5;
    
    // Modifiers
    modifier onlyRegisteredAuditor() {
        require(auditors[msg.sender].isRegistered, "Not a registered auditor");
        _;
    }
    
    modifier validSeverity(uint8 _severity) {
        require(_severity >= 1 && _severity <= MAX_SEVERITY, "Invalid severity level");
        _;
    }
    
    modifier reportExists(uint256 _reportId) {
        require(_reportId <= _reportIds.current() && _reportId > 0, "Report does not exist");
        _;
    }
    
    /**
     * @dev Constructor sets the deployer as owner
     */
    constructor() {
        // Owner is set by Ownable constructor
    }
    
    /**
     * @dev Register as an auditor by paying registration fee
     */
    function registerAuditor() external payable {
        require(!auditors[msg.sender].isRegistered, "Already registered");
        require(msg.value >= REGISTRATION_FEE, "Insufficient registration fee");
        
        auditors[msg.sender] = Auditor({
            isRegistered: true,
            reputation: 100, // Starting reputation
            totalReports: 0,
            registrationTime: block.timestamp
        });
        
        emit AuditorRegistered(msg.sender, block.timestamp);
        
        // Refund excess payment
        if (msg.value > REGISTRATION_FEE) {
            payable(msg.sender).transfer(msg.value - REGISTRATION_FEE);
        }
    }
    
    /**
     * @dev Submit a new audit report
     * @param _contractHash Hash of the audited contract
     * @param _contractName Name of the audited contract
     * @param _ipfsHash IPFS hash containing the full report
     * @param _severity Severity level (1-5)
     * @param _tags Array of tags for categorization
     */
    function submitReport(
        bytes32 _contractHash,
        string memory _contractName,
        string memory _ipfsHash,
        uint8 _severity,
        string[] memory _tags
    ) 
        external 
        payable 
        onlyRegisteredAuditor 
        validSeverity(_severity) 
        nonReentrant 
    {
        require(msg.value >= REPORT_FEE, "Insufficient report fee");
        require(bytes(_contractName).length > 0, "Contract name required");
        require(bytes(_ipfsHash).length > 0, "IPFS hash required");
        require(_tags.length <= 10, "Too many tags");
        
        _reportIds.increment();
        uint256 newReportId = _reportIds.current();
        
        auditReports[newReportId] = AuditReport({
            id: newReportId,
            auditor: msg.sender,
            contractHash: _contractHash,
            contractName: _contractName,
            ipfsHash: _ipfsHash,
            severity: _severity,
            timestamp: block.timestamp,
            isActive: true,
            fee: msg.value
        });
        
        // Update auditor stats
        auditors[msg.sender].totalReports++;
        auditorReports[msg.sender].push(newReportId);
        contractHashes[_contractHash] = true;
        reportTags[newReportId] = _tags;
        
        emit ReportSubmitted(
            newReportId,
            msg.sender,
            _contractHash,
            _severity,
            block.timestamp
        );
        
        // Refund excess payment
        if (msg.value > REPORT_FEE) {
            payable(msg.sender).transfer(msg.value - REPORT_FEE);
        }
    }
    
    /**
     * @dev Update an existing report (only by original auditor)
     * @param _reportId ID of the report to update
     * @param _ipfsHash New IPFS hash
     * @param _severity New severity level
     */
    function updateReport(
        uint256 _reportId,
        string memory _ipfsHash,
        uint8 _severity
    ) 
        external 
        reportExists(_reportId) 
        validSeverity(_severity) 
    {
        AuditReport storage report = auditReports[_reportId];
        require(report.auditor == msg.sender, "Not the report author");
        require(report.isActive, "Report is not active");
        
        report.ipfsHash = _ipfsHash;
        report.severity = _severity;
        
        emit ReportUpdated(_reportId, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Deactivate a report (only owner or auditor)
     * @param _reportId ID of the report to deactivate
     */
    function deactivateReport(uint256 _reportId) 
        external 
        reportExists(_reportId) 
    {
        AuditReport storage report = auditReports[_reportId];
        require(
            msg.sender == owner() || msg.sender == report.auditor,
            "Not authorized to deactivate"
        );
        
        report.isActive = false;
    }
    
    /**
     * @dev Get report details
     * @param _reportId ID of the report
     * @return AuditReport struct
     */
    function getReport(uint256 _reportId) 
        external 
        view 
        reportExists(_reportId) 
        returns (AuditReport memory) 
    {
        return auditReports[_reportId];
    }
    
    /**
     * @dev Get reports by auditor
     * @param _auditor Address of the auditor
     * @return Array of report IDs
     */
    function getReportsByAuditor(address _auditor) 
        external 
        view 
        returns (uint256[] memory) 
    {
        return auditorReports[_auditor];
    }
    
    /**
     * @dev Get total number of reports
     * @return Current report count
     */
    function getTotalReports() external view returns (uint256) {
        return _reportIds.current();
    }
    
    /**
     * @dev Check if contract has been audited
     * @param _contractHash Hash of the contract
     * @return Boolean indicating if audited
     */
    function isContractAudited(bytes32 _contractHash) 
        external 
        view 
        returns (bool) 
    {
        return contractHashes[_contractHash];
    }
    
    /**
     * @dev Get report tags
     * @param _reportId ID of the report
     * @return Array of tags
     */
    function getReportTags(uint256 _reportId) 
        external 
        view 
        reportExists(_reportId) 
        returns (string[] memory) 
    {
        return reportTags[_reportId];
    }
    
    /**
     * @dev Withdraw contract balance (only owner)
     */
    function withdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No funds to withdraw");
        
        payable(owner()).transfer(balance);
    }
    
    /**
     * @dev Emergency pause function (only owner)
     * Note: This is a simplified version - in production use OpenZeppelin's Pausable
     */
    function emergencyPause() external onlyOwner {
        // Implementation would pause contract operations
        // This is a placeholder for demonstration
    }
    
    /**
     * @dev Get auditor information
     * @param _auditor Address of the auditor
     * @return Auditor struct
     */
    function getAuditorInfo(address _auditor) 
        external 
        view 
        returns (Auditor memory) 
    {
        return auditors[_auditor];
    }
    
    /**
     * @dev Fallback function to receive Ether
     */
    receive() external payable {
        // Accept Ether payments
    }
    
    /**
     * @dev Fallback function for unknown function calls
     */
    fallback() external payable {
        revert("Function not found");
    }
}
