// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ProofWork {
    enum BountyStatus { OPEN, CLAIMED, SUBMITTED, PAID, CANCELLED }

    struct Bounty {
        uint256 id;
        address poster;
        uint256 reward;
        string workIpfsHash; 
        BountyStatus status;
        address claimant;
        address judge; // The assigned Judge (Generalist or Custom)
        bytes32 proofHash; 
    }

    uint256 public nextBountyId;
    mapping(uint256 => Bounty) public bounties;
    
    // Address of the ProofWork platform judge
    address public immutable generalistJudge;

    event BountyPosted(uint256 id, address poster, uint256 reward, address judge);
    event BountyClaimed(uint256 id, address claimant);
    event SubmissionReceived(uint256 id, bytes32 proofHash);
    event BountyPaid(uint256 id, address claimant);

    constructor(address _generalistJudge) {
        generalistJudge = _generalistJudge;
    }

    function postBounty(string memory _workIpfsHash, address _customJudge) external payable {
        require(msg.value > 0, "Reward must be > 0");

        uint256 id = nextBountyId++;
        address activeJudge = (_customJudge == address(0)) ? generalistJudge : _customJudge;

        bounties[id] = Bounty({
            id: id,
            poster: msg.sender,
            reward: msg.value,
            workIpfsHash: _workIpfsHash,
            status: BountyStatus.OPEN,
            claimant: address(0),
            judge: activeJudge,
            proofHash: bytes32(0)
        });

        emit BountyPosted(id, msg.sender, msg.value, activeJudge);
    }

    function claimBounty(uint256 id) external {
        Bounty storage b = bounties[id];
        require(b.status == BountyStatus.OPEN, "Bounty not open");
        
        b.status = BountyStatus.CLAIMED;
        b.claimant = msg.sender;
        
        emit BountyClaimed(id, msg.sender);
    }

    function submitProof(uint256 id, bytes32 _proofHash) external {
        Bounty storage b = bounties[id];
        require(b.status == BountyStatus.CLAIMED, "Not claimed");
        require(msg.sender == b.claimant, "Not the claimant");
        
        b.proofHash = _proofHash;
        b.status = BountyStatus.SUBMITTED;
        
        emit SubmissionReceived(id, _proofHash);
    }

    function verifySubmission(uint256 id) external {
        Bounty storage b = bounties[id];
        require(msg.sender == b.judge, "Only judge can verify");
        require(b.status == BountyStatus.SUBMITTED, "Not submitted");
        
        b.status = BountyStatus.PAID;
        payable(b.claimant).transfer(b.reward);
        
        emit BountyPaid(id, b.claimant);
    }

    function cancelBounty(uint256 id) external {
        Bounty storage b = bounties[id];
        require(msg.sender == b.poster, "Only poster can cancel");
        require(b.status == BountyStatus.OPEN, "Only open bounties can be cancelled");
        
        b.status = BountyStatus.CANCELLED;
        payable(b.poster).transfer(b.reward);
    }
}
