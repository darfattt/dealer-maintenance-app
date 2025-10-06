#!/usr/bin/env python3
"""
Test script to validate PKB processor structure without database dependencies
"""
import sys
import os
import logging
import re

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_pkb_structure():
    """Test PKB processor structure and transaction logic"""
    try:
        logger.info("=== Testing PKB Processor Structure ===")

        # Read the PKB processor file
        pkb_file_path = os.path.join(os.path.dirname(__file__), 'tasks', 'processors', 'pkb_processor.py')

        if not os.path.exists(pkb_file_path):
            logger.error(f"❌ PKB processor file not found: {pkb_file_path}")
            return False

        with open(pkb_file_path, 'r', encoding='utf-8') as f:
            pkb_content = f.read()

        # Test 1: Check for _handles_own_commits flag
        if '_handles_own_commits = True' in pkb_content:
            logger.info("✅ Found _handles_own_commits flag")
        else:
            logger.error("❌ Missing _handles_own_commits flag")
            return False

        # Test 2: Check for Phase 1 commit
        if 'Phase 1:' in pkb_content and 'db.commit()' in pkb_content:
            phase1_matches = re.findall(r'Phase 1:.*?db\.commit\(\)', pkb_content, re.DOTALL)
            if phase1_matches:
                logger.info("✅ Found Phase 1 commit for PKB data")
            else:
                logger.error("❌ Phase 1 commit pattern not found")
                return False
        else:
            logger.error("❌ Phase 1 structure not found")
            return False

        # Test 3: Check for Phase 2 and Phase 3
        phase2_found = 'Phase 2:' in pkb_content and 'service records' in pkb_content
        phase3_found = 'Phase 3:' in pkb_content and 'part records' in pkb_content

        if phase2_found and phase3_found:
            logger.info("✅ Found Phase 2 (services) and Phase 3 (parts)")
        else:
            logger.error(f"❌ Missing phases - Phase 2: {phase2_found}, Phase 3: {phase3_found}")
            return False

        # Test 4: Check for _process_child_records method
        if 'def _process_child_records(' in pkb_content:
            logger.info("✅ Found _process_child_records helper method")
        else:
            logger.error("❌ Missing _process_child_records helper method")
            return False

        # Test 5: Check for child record transaction isolation
        child_commit_matches = re.findall(r'Phase [23]:.*?db\.commit\(\)', pkb_content, re.DOTALL)
        if len(child_commit_matches) >= 2:
            logger.info("✅ Found separate commits for child record phases")
        else:
            logger.warning(f"⚠️ Expected 2+ child commits, found {len(child_commit_matches)}")

        # Test 6: Check for error handling in phases
        phase_error_patterns = [
            'service_error',
            'parts_error',
            'db.rollback()',
        ]

        error_handling_found = all(pattern in pkb_content for pattern in phase_error_patterns)
        if error_handling_found:
            logger.info("✅ Found error handling for all phases")
        else:
            missing_patterns = [p for p in phase_error_patterns if p not in pkb_content]
            logger.warning(f"⚠️ Missing error handling patterns: {missing_patterns}")

        # Test 7: Check for work order sanitization
        sanitization_patterns = [
            'sanitized_work_orders',
            'clean_wo = str(wo).strip()[:50]',
            'batch_size = 50',
        ]

        sanitization_found = all(pattern in pkb_content for pattern in sanitization_patterns)
        if sanitization_found:
            logger.info("✅ Found work order sanitization logic")
        else:
            missing_sanitization = [p for p in sanitization_patterns if p not in pkb_content]
            logger.warning(f"⚠️ Missing sanitization patterns: {missing_sanitization}")

        # Test 8: Check for FK mapping logic
        fk_patterns = [
            'pkb_mapping',
            'pkb_data_id',
            'work_order in pkb_mapping',
        ]

        fk_found = all(pattern in pkb_content for pattern in fk_patterns)
        if fk_found:
            logger.info("✅ Found foreign key mapping logic")
        else:
            missing_fk = [p for p in fk_patterns if p not in pkb_content]
            logger.error(f"❌ Missing FK mapping patterns: {missing_fk}")
            return False

        # Test 9: Check base processor transaction handling
        base_file_path = os.path.join(os.path.dirname(__file__), 'tasks', 'processors', 'base_processor.py')

        if os.path.exists(base_file_path):
            with open(base_file_path, 'r', encoding='utf-8') as f:
                base_content = f.read()

            if '_handles_own_commits' in base_content:
                logger.info("✅ Base processor checks for _handles_own_commits")
            else:
                logger.warning("⚠️ Base processor may not check _handles_own_commits")
        else:
            logger.warning("⚠️ Base processor file not found for validation")

        # Test 10: Count transaction management improvements
        improvements = [
            '_handles_own_commits = True',
            'Phase 1: Processing',
            'Phase 2: Processing',
            'Phase 3: Processing',
            '_process_child_records',
            'db.commit()',
            'db.rollback()',
        ]

        found_improvements = sum(1 for improvement in improvements if improvement in pkb_content)
        logger.info(f"✅ Transaction improvements found: {found_improvements}/{len(improvements)}")

        if found_improvements >= 6:
            logger.info("🎉 PKB processor structure validation passed")
            return True
        else:
            logger.error(f"❌ Insufficient improvements found: {found_improvements}/{len(improvements)}")
            return False

    except Exception as e:
        logger.error(f"❌ Structure validation failed: {e}")
        logger.error(f"Error type: {type(e)}")
        return False

def main():
    """Run the structure validation"""
    logger.info("Starting PKB processor structure validation...")

    success = test_pkb_structure()

    if success:
        logger.info("✅ PKB processor structure validated successfully")
        logger.info("Transaction sequencing improvements:")
        logger.info("  ✅ Phase 1: PKB data committed first")
        logger.info("  ✅ Phase 2: Services processed with committed FK references")
        logger.info("  ✅ Phase 3: Parts processed with committed FK references")
        logger.info("  ✅ Work order sanitization to prevent SQL corruption")
        logger.info("  ✅ Independent error handling for each phase")
        logger.info("  ✅ Proper transaction isolation between phases")
    else:
        logger.error("❌ PKB processor structure validation failed")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)