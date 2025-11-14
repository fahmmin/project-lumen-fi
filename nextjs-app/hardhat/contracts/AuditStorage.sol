// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AuditStorage
 * @dev Smart contract for storing audit report hashes and Pinata IPFS links
 */
contract AuditStorage {
    struct AuditRecord {
        bytes32 hash;
        string pinataLink;
        string auditId;
        uint256 timestamp;
        address storedBy;
    }

    AuditRecord[] public audits;
    mapping(string => uint256) public auditIdToIndex;
    mapping(string => bool) public auditIdExists;
    mapping(bytes32 => bool) public hashExists;

    event AuditStored(
        bytes32 indexed hash,
        string pinataLink,
        string auditId,
        uint256 timestamp,
        address indexed storedBy,
        uint256 index
    );

    /**
     * @dev Store an audit record with hash and Pinata link
     * @param _hash SHA-256 hash of the audit report JSON
     * @param _pinataLink IPFS link from Pinata
     * @param _auditId Unique audit identifier
     */
    function storeAudit(
        bytes32 _hash,
        string memory _pinataLink,
        string memory _auditId
    ) public {
        require(_hash != bytes32(0), "Hash cannot be zero");
        require(bytes(_pinataLink).length > 0, "Pinata link cannot be empty");
        require(bytes(_auditId).length > 0, "Audit ID cannot be empty");
        require(!hashExists[_hash], "Hash already exists");
        require(!auditIdExists[_auditId], "Audit ID already exists");

        uint256 index = audits.length;
        audits.push(
            AuditRecord({
                hash: _hash,
                pinataLink: _pinataLink,
                auditId: _auditId,
                timestamp: block.timestamp,
                storedBy: msg.sender
            })
        );

        auditIdToIndex[_auditId] = index;
        auditIdExists[_auditId] = true;
        hashExists[_hash] = true;

        emit AuditStored(
            _hash,
            _pinataLink,
            _auditId,
            block.timestamp,
            msg.sender,
            index
        );
    }

    /**
     * @dev Get audit record by index
     * @param _index Index of the audit record
     * @return AuditRecord The audit record
     */
    function getAudit(uint256 _index) public view returns (AuditRecord memory) {
        require(_index < audits.length, "Index out of bounds");
        return audits[_index];
    }

    /**
     * @dev Get audit record by audit ID
     * @param _auditId The audit ID
     * @return AuditRecord The audit record
     */
    function getAuditById(string memory _auditId) public view returns (AuditRecord memory) {
        uint256 index = auditIdToIndex[_auditId];
        require(index < audits.length, "Audit ID not found");
        require(keccak256(bytes(audits[index].auditId)) == keccak256(bytes(_auditId)), "Audit ID not found");
        return audits[index];
    }

    /**
     * @dev Get total number of audits stored
     * @return uint256 Total count
     */
    function getAuditCount() public view returns (uint256) {
        return audits.length;
    }

    /**
     * @dev Check if a hash exists
     * @param _hash The hash to check
     * @return bool True if hash exists
     */
    function isHashStored(bytes32 _hash) public view returns (bool) {
        return hashExists[_hash];
    }
}

